"""
Authentication & Security Service for CommuniCare.
Handles password hashing (bcrypt), Google Authenticator 2FA (RFC 6238 TOTP via pyotp),
session token issuance, and password recovery.
"""

import os
import secrets
import hashlib
import time
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import bcrypt
import pyotp

from communicare.models import UserAccount, AuthResponse, TwoFactorSetupResponse
from communicare.services.firestore_service import firestore_service

logger = logging.getLogger("communicare.auth")

# In-memory active session token store (token -> user_id)
# Persisted alongside user state in Firestore
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}


class AuthService:
    """
    Manages user registration, login, 2FA Google Authenticator verification,
    and password reset flows with strict data isolation.
    """

    def hash_password(self, password: str) -> str:
        """Hash password securely using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify plain password against bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    def generate_token(self, user_id: str, email: str) -> str:
        """Issue secure cryptographic session token."""
        token = secrets.token_urlsafe(32)
        ACTIVE_SESSIONS[token] = {
            "user_id": user_id,
            "email": email,
            "issued_at": time.time(),
            "expires_at": time.time() + (30 * 24 * 3600)  # 30 days
        }
        return token

    def validate_token(self, token: str) -> Optional[str]:
        """Validate session token and return user_id if valid."""
        if not token:
            return None
        session = ACTIVE_SESSIONS.get(token)
        if session and session["expires_at"] > time.time():
            return session["user_id"]
        return None

    def register_user(self, email: str, password: str, full_name: str) -> Tuple[bool, str, Optional[UserAccount]]:
        """Register a new user account with hashed password."""
        email_clean = email.strip().lower()
        if not email_clean or "@" not in email_clean:
            return False, "Invalid email address format.", None
        if len(password) < 6:
            return False, "Password must be at least 6 characters.", None

        # Check if user already exists
        existing = firestore_service.get_user_by_email(email_clean)
        if existing:
            return False, "An account with this email already exists.", None

        # Generate unique user_id
        safe_prefix = email_clean.split("@")[0]
        user_id = f"user_{safe_prefix}_{secrets.token_hex(4)}"

        hashed_pw = self.hash_password(password)
        user = UserAccount(
            user_id=user_id,
            email=email_clean,
            full_name=full_name.strip() or safe_prefix.title(),
            hashed_password=hashed_pw,
            totp_secret=None,
            totp_enabled=False
        )

        firestore_service.save_user(user)

        # Initialize starter recipient profile for brand-new user workspace
        firestore_service.initialize_user_workspace(user_id, user.full_name)

        logger.info(f"Successfully registered new user: {email_clean} (ID: {user_id})")
        return True, "Account registered successfully.", user

    def authenticate_user(self, email: str, password: str, totp_code: Optional[str] = None) -> AuthResponse:
        """Authenticate user credentials and check Google Authenticator 2FA."""
        email_clean = email.strip().lower()
        user = firestore_service.get_user_by_email(email_clean)
        if not user:
            return AuthResponse(status="error", message="Invalid email or password.")

        if not self.verify_password(password, user.hashed_password):
            return AuthResponse(status="error", message="Invalid email or password.")

        # Check if 2FA (Google Authenticator) is enabled
        if user.totp_enabled and user.totp_secret:
            if not totp_code or not totp_code.strip():
                return AuthResponse(
                    status="2fa_required",
                    user_id=user.user_id,
                    email=user.email,
                    full_name=user.full_name,
                    totp_required=True,
                    totp_enabled=True,
                    message="Please enter your 6-digit Google Authenticator code."
                )

            # Verify TOTP code with 1-step window drift tolerance
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(totp_code.strip(), valid_window=1):
                return AuthResponse(
                    status="error",
                    totp_required=True,
                    totp_enabled=True,
                    message="Invalid 6-digit Google Authenticator code."
                )

        token = self.generate_token(user.user_id, user.email)
        return AuthResponse(
            status="success",
            token=token,
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            totp_required=False,
            totp_enabled=user.totp_enabled,
            message="Logged in successfully."
        )

    def setup_2fa(self, user_id: str) -> Tuple[bool, str, Optional[TwoFactorSetupResponse]]:
        """Generate a new TOTP secret for Google Authenticator."""
        user = firestore_service.get_user_by_id(user_id)
        if not user:
            return False, "User not found.", None

        secret = pyotp.random_base32()
        user.totp_secret = secret
        firestore_service.save_user(user)

        # Generate standard otpauth URI for Google Authenticator / Microsoft Authenticator
        totp = pyotp.TOTP(secret)
        otpauth_url = totp.provisioning_uri(
            name=user.email,
            issuer_name="CommuniCare AAC"
        )

        response = TwoFactorSetupResponse(
            totp_secret=secret,
            otpauth_url=otpauth_url,
            instructions="Enter this secret key in Google Authenticator or scan the provisioning QR code."
        )
        return True, "2FA secret generated successfully.", response

    def enable_2fa(self, user_id: str, totp_code: str) -> Tuple[bool, str]:
        """Verify code and permanently enable 2FA on user account."""
        user = firestore_service.get_user_by_id(user_id)
        if not user or not user.totp_secret:
            return False, "2FA setup has not been initiated."

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(totp_code.strip(), valid_window=1):
            return False, "Invalid 6-digit code. Please verify against your Google Authenticator app."

        user.totp_enabled = True
        firestore_service.save_user(user)
        logger.info(f"Google Authenticator 2FA enabled for user: {user.email}")
        return True, "Google Authenticator 2FA enabled successfully."

    def disable_2fa(self, user_id: str) -> Tuple[bool, str]:
        """Disable 2FA on account."""
        user = firestore_service.get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        user.totp_enabled = False
        user.totp_secret = None
        firestore_service.save_user(user)
        logger.info(f"Google Authenticator 2FA disabled for user: {user.email}")
        return True, "2FA disabled successfully."

    def request_password_reset(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """Generate password reset token."""
        email_clean = email.strip().lower()
        user = firestore_service.get_user_by_email(email_clean)
        if not user:
            # Prevent email enumeration by returning success message
            return True, "If this email is registered, a password reset token has been generated.", None

        token = secrets.token_urlsafe(24)
        user.reset_token = token
        user.reset_token_expires = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        firestore_service.save_user(user)

        logger.info(f"Password reset token issued for {email_clean}: {token}")
        return True, "Password reset token generated.", token

    def reset_password(self, email: str, token: str, new_password: str) -> Tuple[bool, str]:
        """Reset password with verified reset token."""
        email_clean = email.strip().lower()
        user = firestore_service.get_user_by_email(email_clean)
        if not user or not user.reset_token:
            return False, "Invalid or expired reset request."

        if user.reset_token != token.strip():
            return False, "Invalid reset token."

        if user.reset_token_expires:
            exp = datetime.fromisoformat(user.reset_token_expires)
            if datetime.utcnow() > exp:
                return False, "Reset token has expired. Please request a new one."

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."

        user.hashed_password = self.hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        firestore_service.save_user(user)

        logger.info(f"Password reset completed for user: {email_clean}")
        return True, "Password reset successfully. You can now log in with your new password."

    def authenticate_google(self, credential: str) -> AuthResponse:
        """
        Authenticate user with Google OAuth 2.0 Identity Services credential (ID Token JWT).
        Verifies Google token signature, retrieves profile, and auto-provisions user.
        """
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests

            client_id = os.getenv("GOOGLE_CLIENT_ID")
            # Verify the ID token against Google's public certificates
            id_info = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                audience=client_id if client_id else None
            )

            email = id_info.get("email")
            if not email:
                return AuthResponse(status="error", message="Could not extract email from Google credential.")

            email_clean = email.strip().lower()
            name = id_info.get("name") or email_clean.split("@")[0].title()

            # Check if user already exists
            user = firestore_service.get_user_by_email(email_clean)
            if not user:
                # Provision new user from Google profile
                safe_prefix = email_clean.split("@")[0]
                user_id = f"user_google_{safe_prefix}_{secrets.token_hex(4)}"
                dummy_hash = self.hash_password(secrets.token_urlsafe(32))
                user = UserAccount(
                    user_id=user_id,
                    email=email_clean,
                    full_name=name,
                    hashed_password=dummy_hash,
                    totp_secret=None,
                    totp_enabled=False
                )
                firestore_service.save_user(user)
                firestore_service.initialize_user_workspace(user.user_id, user.full_name)
                logger.info(f"Auto-provisioned new Google user: {email_clean} (ID: {user.user_id})")

            token = self.generate_token(user.user_id, user.email)
            return AuthResponse(
                status="success",
                token=token,
                user_id=user.user_id,
                email=user.email,
                full_name=user.full_name,
                totp_required=False,
                totp_enabled=user.totp_enabled,
                message="Google authentication successful."
            )
        except Exception as e:
            logger.error(f"Google OAuth verification failed: {e}")
            return AuthResponse(status="error", message=f"Google authentication failed: {str(e)}")


# Singleton instance
auth_service = AuthService()

