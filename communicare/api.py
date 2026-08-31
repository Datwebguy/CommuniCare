"""
FastAPI Route Handlers for CommuniCare.
Exposes REST endpoints for autonomous board generation, memory management,
user authentication, Google Authenticator 2FA, password recovery, multi tenant isolation, and health checks.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Header, status, Depends
from communicare.models import (
    CaregiverMessageRequest,
    AACBoardResponse,
    RecipientProfile,
    FeedbackRequest,
    FeedbackResponse,
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    GoogleAuthRequest
)
from communicare.agent.pipeline import agent_orchestrator
from communicare.services.firestore_service import firestore_service
from communicare.services.symbol_library import symbol_resolver
from communicare.services.gemini_service import gemini_service
from communicare.services.auth_service import auth_service

router = APIRouter(prefix="/api", tags=["CommuniCare Agent"])


def get_current_caregiver_id(
    authorization: Optional[str] = Header(None),
    x_caregiver_id: Optional[str] = Header(None, alias="X-Caregiver-ID"),
    caregiver_id: Optional[str] = Query(None)
) -> str:
    """
    Resolves the authenticated caregiver ID from session Bearer token,
    explicit header, or query param, defaulting safely to 'caregiver_primary'.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_id = auth_service.validate_token(token)
        if user_id:
            return user_id
    if x_caregiver_id and x_caregiver_id.strip():
        return x_caregiver_id.strip()
    if caregiver_id and caregiver_id.strip():
        return caregiver_id.strip()
    return "caregiver_primary"


# =========================================================================
# USER AUTHENTICATION & GOOGLE AUTHENTICATOR 2FA ENDPOINTS
# =========================================================================

@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """Register a new user account with hashed password and isolated workspace."""
    success, message, user = auth_service.register_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    if not success or not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    token = auth_service.generate_token(user.user_id, user.email)
    return AuthResponse(
        status="success",
        token=token,
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        totp_required=False,
        totp_enabled=False,
        message=message
    )


@router.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest):
    """Authenticate user with email, password, and optional Google Authenticator TOTP."""
    response = auth_service.authenticate_user(
        email=request.email,
        password=request.password,
        totp_code=request.totp_code
    )
    if response.status == "error":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=response.message)
    return response


@router.post("/auth/google", response_model=AuthResponse)
def google_login(request: GoogleAuthRequest):
    """Authenticate or auto-provision user using Google OAuth 2.0 Identity Token."""
    response = auth_service.authenticate_google(request.credential)
    if response.status == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    return response


@router.post("/auth/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """Request a password reset token for account recovery."""
    success, message, token = auth_service.request_password_reset(request.email)
    return {
        "status": "success",
        "message": message,
        "reset_token_preview": token  # Returned for ease of testing & demonstration
    }


@router.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Reset account password using verified reset token."""
    success, message = auth_service.reset_password(
        email=request.email,
        token=request.reset_token,
        new_password=request.new_password
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"status": "success", "message": message}


@router.get("/auth/me")
def get_current_user_profile(caregiver_id: str = Depends(get_current_caregiver_id)):
    """Retrieve profile and 2FA status for currently authenticated user."""
    user = firestore_service.get_user_by_id(caregiver_id)
    if not user:
        # Demo / default workspace profile
        return {
            "user_id": caregiver_id,
            "email": f"{caregiver_id}@communicare.local",
            "full_name": caregiver_id.replace("_", " ").title(),
            "totp_enabled": False
        }
    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "totp_enabled": user.totp_enabled
    }


@router.post("/auth/2fa/setup", response_model=TwoFactorSetupResponse)
def setup_two_factor(caregiver_id: str = Depends(get_current_caregiver_id)):
    """Generate TOTP secret key for Google Authenticator."""
    success, message, setup_data = auth_service.setup_2fa(caregiver_id)
    if not success or not setup_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return setup_data


@router.post("/auth/2fa/enable")
def enable_two_factor(
    request: TwoFactorVerifyRequest,
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """Verify 6-digit code and permanently activate Google Authenticator 2FA."""
    success, message = auth_service.enable_2fa(caregiver_id, request.totp_code)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"status": "success", "message": message}


@router.post("/auth/2fa/disable")
def disable_two_factor(caregiver_id: str = Depends(get_current_caregiver_id)):
    """Deactivate 2FA for the account."""
    success, message = auth_service.disable_2fa(caregiver_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"status": "success", "message": message}


# =========================================================================
# AAC AGENT & BOARD GENERATION
# =========================================================================

@router.post("/generate-board", response_model=AACBoardResponse, status_code=status.HTTP_200_OK)
def generate_aac_board(
    request: CaregiverMessageRequest,
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """
    Autonomous pipeline endpoint: Converts raw caregiver message into an
    accessible high contrast AAC picture symbol board with multi tenant scoping.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caregiver message cannot be empty."
        )

    request.caregiver_id = caregiver_id

    try:
        response = agent_orchestrator.process_caregiver_message(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}"
        )


@router.get("/recipients", response_model=List[RecipientProfile])
def list_recipients(caregiver_id: str = Depends(get_current_caregiver_id)):
    """List registered care recipients and their learned profiles for the active caregiver."""
    return firestore_service.list_recipients(caregiver_id=caregiver_id)


@router.get("/recipients/{recipient_id}", response_model=RecipientProfile)
def get_recipient(
    recipient_id: str,
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """Get profile and memory details for a specific care recipient."""
    return firestore_service.get_recipient_profile(recipient_id=recipient_id, caregiver_id=caregiver_id)


@router.post("/recipients", response_model=RecipientProfile, status_code=status.HTTP_200_OK)
def save_recipient(
    profile: RecipientProfile,
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """Create or update a care recipient profile dynamically."""
    profile.caregiver_id = caregiver_id
    firestore_service.save_recipient_profile(profile)
    return profile


@router.delete("/recipients/{recipient_id}")
def delete_recipient(
    recipient_id: str,
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """Delete a care recipient profile safely."""
    success = firestore_service.delete_recipient_profile(recipient_id=recipient_id, caregiver_id=caregiver_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    return {"status": "success", "message": f"Deleted recipient {recipient_id}"}


@router.post("/feedback", response_model=FeedbackResponse)
def submit_caregiver_feedback(
    feedback: FeedbackRequest,
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """
    Caregiver feedback loop: records what worked well, reinforces successful vocabulary,
    or stores personalized symbol overrides in Firestore.
    """
    feedback.caregiver_id = caregiver_id
    words = [feedback.word] if feedback.word else []
    updated_profile = firestore_service.record_interaction(
        recipient_id=feedback.recipient_id,
        words=words,
        action=feedback.action,
        preferred_symbol=feedback.preferred_symbol,
        caregiver_id=caregiver_id
    )

    return FeedbackResponse(
        status="success",
        message=f"Memory updated for {updated_profile.name} (Action: {feedback.action})",
        recipient_id=feedback.recipient_id,
        updated_memory_summary={
            "learned_vocabulary_count": len(updated_profile.learned_vocabulary),
            "success_history": updated_profile.success_history,
            "preferred_symbol_mappings": updated_profile.preferred_symbol_mappings
        }
    )


@router.get("/presets")
def get_demo_presets(caregiver_id: str = Depends(get_current_caregiver_id)):
    """Return dynamic care routine presets stored in Firestore persistent layer."""
    return firestore_service.list_presets(caregiver_id=caregiver_id)


@router.post("/presets")
def save_custom_preset(
    preset: Dict[str, Any],
    caregiver_id: str = Depends(get_current_caregiver_id)
):
    """Save a dynamic caregiver scenario preset."""
    if not preset.get("title") or not preset.get("message"):
        raise HTTPException(status_code=400, detail="Title and message are required.")
    success = firestore_service.save_preset(preset, caregiver_id=caregiver_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save preset.")
    return {"status": "success", "preset": preset}


@router.get("/symbols/search")
def search_symbols(q: str = Query(..., min_length=1)):
    """Search available AAC pictograms and vector icons dynamically."""
    return symbol_resolver.search_symbols(q)


@router.get("/health")
def health_check():
    """System health check and diagnostic status."""
    return {
        "status": "healthy",
        "service": "CommuniCare Agent Platform",
        "version": "1.0.0",
        "system_status": "Operational",
        "gemini_active": gemini_service.client is not None,
        "gemini_model": gemini_service.model_name,
        "firestore_mode": "Google Cloud Firestore" if firestore_service._is_live_firestore else "Local Persistent JSON State",
        "cloud_project": firestore_service.project_id or "local",
        "firestore_error": firestore_service._init_error,
        "firestore_json_chars": firestore_service._sa_json_len,
        "firestore_json_prefix": firestore_service._sa_json_prefix,
    }
