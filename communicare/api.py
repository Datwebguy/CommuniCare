"""
FastAPI Route Handlers for CommuniCare.
Exposes REST endpoints for autonomous board generation, memory management,
feedback loops, and health checks.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from communicare.models import (
    CaregiverMessageRequest,
    AACBoardResponse,
    RecipientProfile,
    FeedbackRequest,
    FeedbackResponse
)
from communicare.agent.pipeline import agent_orchestrator
from communicare.services.firestore_service import firestore_service
from communicare.services.symbol_library import symbol_resolver
from communicare.services.gemini_service import gemini_service

router = APIRouter(prefix="/api", tags=["CommuniCare Agent"])

# Curated Presets for Quick Caregiver Demos
DEMO_PRESETS = [
    {
        "id": "morning_breakfast_walk",
        "title": "Morning Routine & Breakfast",
        "description": "Medicine, breakfast choices, and park walk",
        "recipient_id": "leo_care",
        "message": "Good morning Leo! Please take your medicine with a glass of water. Then we will eat warm pancakes for breakfast and take a walk to the park to see the dogs."
    },
    {
        "id": "medical_checkin",
        "title": "Medical & Sensory Check-in",
        "description": "Therapy session, feeling check, and hydration",
        "recipient_id": "maya_adult",
        "message": "Hello Maya, the doctor will visit soon. Let me know if you feel hurt or tired, and please drink some water before we listen to quiet music."
    },
    {
        "id": "school_transition",
        "title": "School Transition & Lunch",
        "description": "Getting dressed, riding the school bus, and lunchtime",
        "recipient_id": "leo_care",
        "message": "Time to put on your clothes and shoes. The yellow school bus is coming soon to take us to school. We have a lunch box with an apple and juice!"
    },
    {
        "id": "evening_bedtime",
        "title": "Evening Hygiene & Bedtime",
        "description": "Bathroom, brushing teeth, and bedtime book",
        "recipient_id": "leo_care",
        "message": "It is nighttime. Let's use the bathroom, wash hands, and brush teeth. Then we can read a book in bed and go to sleep."
    }
]


@router.post("/generate-board", response_model=AACBoardResponse, status_code=status.HTTP_200_OK)
def generate_aac_board(request: CaregiverMessageRequest):
    """
    Autonomous pipeline endpoint: Converts raw caregiver message into an
    accessible, high-contrast AAC picture symbol board.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caregiver message cannot be empty."
        )

    try:
        response = agent_orchestrator.process_caregiver_message(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}"
        )


@router.get("/recipients", response_model=List[RecipientProfile])
def list_recipients():
    """List all registered care recipients and their learned profiles."""
    return firestore_service.list_recipients()


@router.get("/recipients/{recipient_id}", response_model=RecipientProfile)
def get_recipient(recipient_id: str):
    """Get profile and memory details for a specific care recipient."""
    return firestore_service.get_recipient_profile(recipient_id)


@router.post("/recipients", response_model=RecipientProfile, status_code=status.HTTP_200_OK)
def save_recipient(profile: RecipientProfile):
    """Create or update a care recipient profile."""
    firestore_service.save_recipient_profile(profile)
    return profile


@router.post("/feedback", response_model=FeedbackResponse)
def submit_caregiver_feedback(feedback: FeedbackRequest):
    """
    Caregiver feedback loop: records what worked well, reinforces successful vocabulary,
    or stores personalized symbol overrides in Firestore.
    """
    words = [feedback.word] if feedback.word else []
    updated_profile = firestore_service.record_interaction(
        recipient_id=feedback.recipient_id,
        words=words,
        action=feedback.action,
        preferred_symbol=feedback.preferred_symbol
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
def get_demo_presets():
    """Return pre-configured realistic caregiver scenarios for instant testing."""
    return DEMO_PRESETS


@router.get("/symbols/search")
def search_symbols(q: str = Query(..., min_length=1)):
    """Search available AAC pictograms and vector icons."""
    return symbol_resolver.search_symbols(q)


@router.get("/health")
def health_check():
    """Google Cloud Run health check and system diagnostic status."""
    return {
        "status": "healthy",
        "service": "CommuniCare Agent",
        "version": "1.0.0",
        "track": "Taskmaster (Google All Things Agentic Hackathon)",
        "gemini_active": gemini_service.client is not None,
        "gemini_model": gemini_service.model_name,
        "firestore_mode": "Google Cloud Firestore" if firestore_service._is_live_firestore else "Local Persistent JSON State",
        "cloud_project": firestore_service.project_id or "local"
    }
