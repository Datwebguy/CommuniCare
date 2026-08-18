"""
Firestore State and Memory Service for CommuniCare.
Manages per-recipient AAC vocabulary profiles, symbol preferences, and multi-turn adaptation.
Supports live Google Cloud Firestore with zero-config local persistence fallback.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from communicare.models import RecipientProfile

logger = logging.getLogger("communicare.firestore")

# Default profiles for demonstration and testing
DEFAULT_PROFILES: Dict[str, Dict] = {
    "leo_care": {
        "recipient_id": "leo_care",
        "name": "Leo (Age 7)",
        "age_group": "child",
        "vocabulary_level": "basic",
        "max_board_cards": 6,
        "high_contrast_mode": True,
        "color_coding_enabled": True,
        "preferred_symbol_mappings": {
            "medicine": "medicine",
            "bathroom": "bathroom",
            "pancakes": "pancakes"
        },
        "learned_vocabulary": ["eat", "drink", "walk", "medicine", "park", "dog", "happy"],
        "success_history": {
            "medicine": 4,
            "walk": 6,
            "park": 5,
            "pancakes": 3,
            "water": 8
        },
        "caregiver_notes": "Responds best to high contrast yellow and orange cards. Loves morning walk routines.",
        "last_interaction": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    },
    "maya_adult": {
        "recipient_id": "maya_adult",
        "name": "Maya (Adult - Stroke Recovery)",
        "age_group": "adult",
        "vocabulary_level": "intermediate",
        "max_board_cards": 8,
        "high_contrast_mode": True,
        "color_coding_enabled": True,
        "preferred_symbol_mappings": {
            "doctor": "doctor",
            "water": "water",
            "quiet": "quiet"
        },
        "learned_vocabulary": ["doctor", "water", "quiet", "tired", "help", "music", "snack"],
        "success_history": {
            "doctor": 2,
            "water": 5,
            "quiet": 3
        },
        "caregiver_notes": "Prefers clear realistic pictograms. Needs calm pacing during physical therapy sessions.",
        "last_interaction": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
}


class FirestoreService:
    """
    State manager handling care recipient memory, vocabulary profiles,
    and adaptive learning across multiple communication sessions.
    """

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.local_storage_dir = Path("./data")
        self.local_storage_file = self.local_storage_dir / "recipient_profiles.json"
        self.db = None
        self._is_live_firestore = False
        
        self._init_backend()

    def _init_backend(self):
        """Attempt connection to Google Cloud Firestore, fallback to local JSON engine."""
        # Check if Google credentials or project are present
        if self.project_id and (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("K_SERVICE")):
            try:
                from google.cloud import firestore
                self.db = firestore.Client(project=self.project_id)
                self._is_live_firestore = True
                logger.info(f"Connected to live Google Cloud Firestore project: {self.project_id}")
                return
            except Exception as e:
                logger.warning(f"Could not connect to live Firestore ({e}). Using persistent local fallback.")

        # Local persistence mode
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)
        if not self.local_storage_file.exists():
            with open(self.local_storage_file, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_PROFILES, f, indent=2)
            logger.info("Initialized local persistent recipient memory with default profiles.")

    def get_recipient_profile(self, recipient_id: str) -> RecipientProfile:
        """Fetch recipient profile by ID."""
        if self._is_live_firestore and self.db:
            try:
                doc = self.db.collection("recipient_profiles").document(recipient_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    return RecipientProfile(**data)
            except Exception as e:
                logger.error(f"Error fetching from live Firestore: {e}")

        # Local JSON backend lookup
        profiles = self._read_local_profiles()
        if recipient_id in profiles:
            return RecipientProfile(**profiles[recipient_id])
        
        # Create a new profile if not found
        new_profile = RecipientProfile(
            recipient_id=recipient_id,
            name=recipient_id.replace("_", " ").title(),
            vocabulary_level="basic",
            max_board_cards=6
        )
        self.save_recipient_profile(new_profile)
        return new_profile

    def save_recipient_profile(self, profile: RecipientProfile) -> bool:
        """Save or update recipient profile in persistent storage."""
        profile.updated_at = datetime.utcnow().isoformat()
        profile_dict = profile.model_dump()

        if self._is_live_firestore and self.db:
            try:
                self.db.collection("recipient_profiles").document(profile.recipient_id).set(profile_dict)
                return True
            except Exception as e:
                logger.error(f"Error saving to live Firestore: {e}")

        # Local JSON backend
        profiles = self._read_local_profiles()
        profiles[profile.recipient_id] = profile_dict
        self._write_local_profiles(profiles)
        return True

    def list_recipients(self) -> List[RecipientProfile]:
        """List all available recipient profiles."""
        if self._is_live_firestore and self.db:
            try:
                docs = self.db.collection("recipient_profiles").stream()
                return [RecipientProfile(**doc.to_dict()) for doc in docs]
            except Exception as e:
                logger.error(f"Error listing from live Firestore: {e}")

        profiles = self._read_local_profiles()
        return [RecipientProfile(**data) for data in profiles.values()]

    def record_interaction(
        self,
        recipient_id: str,
        words: List[str],
        action: str = "used",
        preferred_symbol: Optional[str] = None
    ) -> RecipientProfile:
        """
        Updates recipient memory with used words, boosts success counts,
        and saves custom symbol mappings.
        """
        profile = self.get_recipient_profile(recipient_id)
        profile.last_interaction = datetime.utcnow().isoformat()

        # Update learned vocabulary list
        for word in words:
            word_lower = word.lower()
            if word_lower not in profile.learned_vocabulary:
                profile.learned_vocabulary.append(word_lower)
            
            if action in ["worked_well", "used"]:
                profile.success_history[word_lower] = profile.success_history.get(word_lower, 0) + 1

        if preferred_symbol and words:
            target_word = words[0].lower()
            profile.preferred_symbol_mappings[target_word] = preferred_symbol

        self.save_recipient_profile(profile)
        return profile

    def _read_local_profiles(self) -> Dict[str, Dict]:
        try:
            if self.local_storage_file.exists():
                with open(self.local_storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading local profile store: {e}")
        return DEFAULT_PROFILES.copy()

    def _write_local_profiles(self, data: Dict[str, Dict]):
        try:
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)
            with open(self.local_storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to local profile store: {e}")


# Singleton instance
firestore_service = FirestoreService()
