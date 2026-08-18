"""
End to End tests for the CommuniCare Autonomous Agent Pipeline.
Verifies message ingestion, simplification, symbol mapping, board assembly, and memory persistence.
"""

import pytest
from communicare.agent.pipeline import agent_orchestrator
from communicare.models import CaregiverMessageRequest, GrammarCategory
from communicare.services.firestore_service import firestore_service


def test_agent_pipeline_morning_routine():
    """Verify autonomous pipeline generates valid AAC board for morning care message."""
    request = CaregiverMessageRequest(
        message="Good morning Leo! Please take your medicine with a glass of water, then eat pancakes for breakfast.",
        recipient_id="leo_care",
        simplify_style="core_words"
    )

    response = agent_orchestrator.process_caregiver_message(request)

    # 1. Assert response structure
    assert response.board_id.startswith("board_")
    assert response.recipient_id == "leo_care"
    assert len(response.cards) > 0
    assert len(response.pipeline_trace) == 5

    # 2. Check pipeline trace steps
    step_names = [t.step_name for t in response.pipeline_trace]
    assert "Profile and Memory Lookup" in step_names
    assert "Gemini Language Simplification" in step_names
    assert "AAC Symbol Resolution" in step_names
    assert "Board Layout and Fitzgerald Composition" in step_names
    assert "Memory State Update" in step_names

    # 3. Check cards contain key words
    card_words = [c.word for c in response.cards]
    assert any("MEDICINE" in w for w in card_words)
    assert any("WATER" in w for w in card_words)
    assert any("PANCAKES" in w for w in card_words)

    # 4. Check that cards have Fitzgerald Key styling
    for card in response.cards:
        assert card.color_code.startswith("#")
        assert card.bg_color.startswith("#")


def test_agent_pipeline_multi_turn_adaptation():
    """Verify system adapts over multiple messages using learned Firestore preferences."""
    test_id = "adaptive_demo_user"
    profile = firestore_service.get_recipient_profile(test_id)
    profile.preferred_symbol_mappings["doctor"] = "custom_doctor_icon"
    firestore_service.save_recipient_profile(profile)

    request = CaregiverMessageRequest(
        message="Hello! The doctor will visit us today to help check your health.",
        recipient_id=test_id
    )

    response = agent_orchestrator.process_caregiver_message(request)
    assert any("DOCTOR" in c.word for c in response.cards)
    assert len(response.personalized_adaptations_applied) > 0
    assert any("doctor" in a.lower() for a in response.personalized_adaptations_applied)
