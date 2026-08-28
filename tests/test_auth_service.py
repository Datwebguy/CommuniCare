"""
Unit and integration tests for CommuniCare User Authentication and Google Authenticator 2FA.
Verifies registration, password hashing, login, 2FA TOTP verification, password reset,
and multi tenant Firestore data isolation.
"""

import uuid
import pytest
import pyotp
from communicare.services.auth_service import auth_service
from communicare.services.firestore_service import firestore_service
from communicare.models import RecipientProfile


def test_user_registration_and_password_hashing():
    """Test creating user account with secure hashed password."""
    uid = uuid.uuid4().hex[:8]
    email = f"dr_watson_{uid}@clinic.com"
    pw = "SecretMedPass123!"
    name = "Dr. John Watson"

    success, msg, user = auth_service.register_user(email, pw, name)
    assert success is True
    assert user is not None
    assert user.email == email
    assert user.full_name == name
    assert user.hashed_password != pw  # Must be hashed
    assert auth_service.verify_password(pw, user.hashed_password) is True
    assert auth_service.verify_password("WrongPassword", user.hashed_password) is False


def test_user_authentication_success_and_failure():
    """Test logging in with valid and invalid credentials."""
    uid = uuid.uuid4().hex[:8]
    email = f"sarah_slp_{uid}@therapy.org"
    pw = "SpeechTherapy2026"
    name = "Sarah SLP"

    auth_service.register_user(email, pw, name)

    # Valid credentials
    auth_resp = auth_service.authenticate_user(email, pw)
    assert auth_resp.status == "success"
    assert auth_resp.token is not None
    assert auth_service.validate_token(auth_resp.token) == auth_resp.user_id

    # Invalid password
    bad_resp = auth_service.authenticate_user(email, "WrongPass")
    assert bad_resp.status == "error"
    assert bad_resp.token is None


def test_google_authenticator_2fa_flow():
    """Test full TOTP 2FA setup, challenge, and verification."""
    uid = uuid.uuid4().hex[:8]
    email = f"secure_care_{uid}@hospital.org"
    pw = "SuperSecure123"
    name = "Nurse Claire"

    success, _, user = auth_service.register_user(email, pw, name)
    assert success is True
    user_id = user.user_id

    # 1. Setup 2FA
    setup_ok, setup_msg, setup_data = auth_service.setup_2fa(user_id)
    assert setup_ok is True
    assert setup_data.totp_secret is not None
    assert "otpauth://" in setup_data.otpauth_url

    # 2. Generate valid TOTP code
    totp = pyotp.TOTP(setup_data.totp_secret)
    valid_code = totp.now()

    # 3. Enable 2FA with valid code
    enable_ok, _ = auth_service.enable_2fa(user_id, valid_code)
    assert enable_ok is True

    # 4. Attempt login without code -> Must require 2FA
    login_step1 = auth_service.authenticate_user(email, pw)
    assert login_step1.status == "2fa_required"
    assert login_step1.totp_required is True

    # 5. Attempt login with bad 2FA code -> Must fail
    login_step2_bad = auth_service.authenticate_user(email, pw, totp_code="000000")
    assert login_step2_bad.status == "error"

    # 6. Attempt login with fresh valid 2FA code -> Must succeed
    fresh_code = totp.now()
    login_step2_ok = auth_service.authenticate_user(email, pw, totp_code=fresh_code)
    assert login_step2_ok.status == "success"
    assert login_step2_ok.token is not None


def test_password_reset_flow():
    """Test forgot password token generation and password reset."""
    uid = uuid.uuid4().hex[:8]
    email = f"forgetful_user_{uid}@clinic.com"
    pw = "OldPassword123"
    new_pw = "BrandNewPassword456"

    auth_service.register_user(email, pw, "Forgetful User")

    # Request reset
    req_ok, req_msg, token = auth_service.request_password_reset(email)
    assert req_ok is True
    assert token is not None

    # Reset password with token
    reset_ok, reset_msg = auth_service.reset_password(email, token, new_pw)
    assert reset_ok is True

    # Verify old password fails and new password succeeds
    assert auth_service.authenticate_user(email, pw).status == "error"
    assert auth_service.authenticate_user(email, new_pw).status == "success"


def test_strict_multi_tenant_user_isolation():
    """Verify that User A cannot see or access User B's care recipient records."""
    uid_a = uuid.uuid4().hex[:8]
    uid_b = uuid.uuid4().hex[:8]
    # Register User A
    _, _, user_a = auth_service.register_user(f"caregiver_a_{uid_a}@test.com", "Password123", "Caregiver A")
    # Register User B
    _, _, user_b = auth_service.register_user(f"caregiver_b_{uid_b}@test.com", "Password123", "Caregiver B")

    assert user_a is not None
    assert user_b is not None

    # Save private recipient for User A
    rec_a = RecipientProfile(
        recipient_id=f"private_patient_a_{uid_a}",
        caregiver_id=user_a.user_id,
        name="Patient A (Private)",
        vocabulary_level="basic"
    )
    firestore_service.save_recipient_profile(rec_a)

    # Save private recipient for User B
    rec_b = RecipientProfile(
        recipient_id=f"private_patient_b_{uid_b}",
        caregiver_id=user_b.user_id,
        name="Patient B (Private)",
        vocabulary_level="basic"
    )
    firestore_service.save_recipient_profile(rec_b)

    # List recipients for User A
    list_a = firestore_service.list_recipients(caregiver_id=user_a.user_id)
    rec_ids_a = [r.recipient_id for r in list_a]
    assert rec_a.recipient_id in rec_ids_a
    assert rec_b.recipient_id not in rec_ids_a  # User A CANNOT see User B's patient!

    # List recipients for User B
    list_b = firestore_service.list_recipients(caregiver_id=user_b.user_id)
    rec_ids_b = [r.recipient_id for r in list_b]
    assert rec_b.recipient_id in rec_ids_b
    assert rec_a.recipient_id not in rec_ids_b  # User B CANNOT see User A's patient!
