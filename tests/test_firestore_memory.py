"""
Unit tests for Firestore State & Memory Management.
Verifies recipient profile persistence, vocabulary learning, and preference adaptation.
"""

import pytest
from communicare.services.firestore_service import firestore_service
from communicare.models import RecipientProfile


def test_get_and_save_recipient_profile():
    """Verify getting default recipient profile and saving modifications."""
    profile = firestore_service.get_recipient_profile("leo_care")
    assert profile.recipient_id == "leo_care"
    assert profile.name == "Leo (Age 7)"
    assert profile.vocabulary_level == "basic"

    # Modify and save
    profile.caregiver_notes = "Updated test notes for Leo"
    firestore_service.save_recipient_profile(profile)

    # Re-fetch
    updated = firestore_service.get_recipient_profile("leo_care")
    assert updated.caregiver_notes == "Updated test notes for Leo"


def test_record_interaction_and_learn_vocabulary():
    """Verify recording board usage updates learned vocabulary and success counters."""
    test_id = "test_user_memory"
    profile = RecipientProfile(
        recipient_id=test_id,
        name="Test User",
        vocabulary_level="basic",
        max_board_cards=5
    )
    firestore_service.save_recipient_profile(profile)

    # Record first interaction
    firestore_service.record_interaction(
        recipient_id=test_id,
        words=["medicine", "water", "pancakes"],
        action="worked_well"
    )

    p1 = firestore_service.get_recipient_profile(test_id)
    assert "medicine" in p1.learned_vocabulary
    assert p1.success_history.get("medicine") == 1
    assert p1.success_history.get("water") == 1

    # Record second interaction reinforcing 'medicine'
    firestore_service.record_interaction(
        recipient_id=test_id,
        words=["medicine"],
        action="worked_well",
        preferred_symbol="medicine_custom_icon"
    )

    p2 = firestore_service.get_recipient_profile(test_id)
    assert p2.success_history.get("medicine") == 2
    assert p2.preferred_symbol_mappings.get("medicine") == "medicine_custom_icon"


def test_list_recipients():
    """Verify listing all recipient profiles."""
    recipients = firestore_service.list_recipients()
    assert len(recipients) >= 2
    ids = [r.recipient_id for r in recipients]
    assert "leo_care" in ids
    assert "maya_adult" in ids
