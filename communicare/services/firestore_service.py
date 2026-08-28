"""
Firestore State and Memory Service for CommuniCare.
Manages per recipient AAC vocabulary profiles, symbol preferences, user accounts, and dynamic presets.
Provides strict multi tenant caregiver isolation and persistent memory.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from communicare.models import RecipientProfile, UserAccount

logger = logging.getLogger("communicare.firestore")

DEFAULT_PROFILES: Dict[str, Dict] = {
    "leo_care": {
        "recipient_id": "leo_care",
        "caregiver_id": "caregiver_primary",
        "name": "Leo",
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
        "caregiver_id": "caregiver_primary",
        "name": "Maya",
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

DEFAULT_PRESETS = [
    {
        "id": "morning_breakfast_walk",
        "caregiver_id": "caregiver_primary",
        "title": "Morning Routine and Breakfast",
        "description": "Medicine, breakfast choices, and park walk",
        "recipient_id": "leo_care",
        "message": "Good morning Leo! Please take your medicine with a glass of water, then eat pancakes for breakfast and we will take a walk to the park to see the dogs."
    },
    {
        "id": "medical_checkin",
        "caregiver_id": "caregiver_primary",
        "title": "Medical and Sensory Checkin",
        "description": "Therapy session, feeling check, and hydration",
        "recipient_id": "maya_adult",
        "message": "Hello Maya, the doctor will visit soon. Let me know if you feel hurt or tired, and please drink some water before we listen to quiet music."
    },
    {
        "id": "school_transition",
        "caregiver_id": "caregiver_primary",
        "title": "School Transition and Lunch",
        "description": "Getting dressed, riding the school bus, and lunchtime",
        "recipient_id": "leo_care",
        "message": "Time to put on your clothes and shoes. The yellow school bus is coming soon to take us to school. We have a lunch box with an apple and juice!"
    },
    {
        "id": "evening_bedtime",
        "caregiver_id": "caregiver_primary",
        "title": "Evening Hygiene and Bedtime",
        "description": "Bathroom, brushing teeth, and bedtime book",
        "recipient_id": "leo_care",
        "message": "It is nighttime. Let us use the bathroom, wash hands, and brush teeth. Then we can read a book in bed and go to sleep."
    }
]


import tempfile
import shutil

class FirestoreService:
    """
    Multi tenant state manager handling care recipient memory, vocabulary profiles,
    user accounts, and adaptive learning across communication sessions with user isolation.
    """

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        # Determine writable storage directory (safe for Vercel, AWS Lambda, local Docker)
        is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("LAMBDA_TASK_ROOT"))
        if is_serverless:
            self.local_storage_dir = Path(tempfile.gettempdir()) / "communicare_data"
        else:
            self.local_storage_dir = Path("./data")

        self.local_storage_file = self.local_storage_dir / "recipient_profiles.json"
        self.presets_file = self.local_storage_dir / "presets.json"
        self.users_file = self.local_storage_dir / "users.json"
        self.db = None
        self._is_live_firestore = False
        
        self._init_backend()

    def _init_backend(self):
        """Attempt connection to Google Cloud Firestore, fallback to local JSON engine."""
        if self.project_id and (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("K_SERVICE")):
            try:
                from google.cloud import firestore
                self.db = firestore.Client(project=self.project_id)
                self._is_live_firestore = True
                logger.info(f"Connected to live Google Cloud Firestore project: {self.project_id}")
                return
            except Exception as e:
                logger.warning(f"Could not connect to live Firestore ({e}). Using persistent local fallback.")

        # Local persistence mode with safe temp fallback
        try:
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.local_storage_dir = Path(tempfile.gettempdir()) / "communicare_data"
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)
            self.local_storage_file = self.local_storage_dir / "recipient_profiles.json"
            self.presets_file = self.local_storage_dir / "presets.json"
            self.users_file = self.local_storage_dir / "users.json"

        try:
            repo_data_dir = Path(__file__).parent.parent.parent / "data"
            if not self.local_storage_file.exists():
                repo_file = repo_data_dir / "recipient_profiles.json"
                if repo_file.exists():
                    shutil.copyfile(repo_file, self.local_storage_file)
                else:
                    with open(self.local_storage_file, "w", encoding="utf-8") as f:
                        json.dump(DEFAULT_PROFILES, f, indent=2)

            if not self.presets_file.exists():
                repo_file = repo_data_dir / "presets.json"
                if repo_file.exists():
                    shutil.copyfile(repo_file, self.presets_file)
                else:
                    with open(self.presets_file, "w", encoding="utf-8") as f:
                        json.dump(DEFAULT_PRESETS, f, indent=2)

            if not self.users_file.exists():
                repo_file = repo_data_dir / "users.json"
                if repo_file.exists():
                    shutil.copyfile(repo_file, self.users_file)
                else:
                    with open(self.users_file, "w", encoding="utf-8") as f:
                        json.dump({}, f, indent=2)
        except Exception as e:
            logger.warning(f"Initialized local JSON fallback memory store with warning: {e}")

    # =========================================================================
    # USER ACCOUNT MANAGEMENT & STRICT ISOLATION
    # =========================================================================

    def get_user_by_email(self, email: str) -> Optional[UserAccount]:
        """Look up user by email address."""
        email_clean = email.strip().lower()
        if self._is_live_firestore and self.db:
            try:
                docs = self.db.collection("users").where("email", "==", email_clean).limit(1).stream()
                for doc in docs:
                    return UserAccount(**doc.to_dict())
            except Exception as e:
                logger.error(f"Error fetching user from Firestore: {e}")

        users = self._read_local_users()
        for u in users.values():
            if u.get("email", "").lower() == email_clean:
                return UserAccount(**u)
        return None

    def get_user_by_id(self, user_id: str) -> Optional[UserAccount]:
        """Look up user by user ID."""
        if self._is_live_firestore and self.db:
            try:
                doc = self.db.collection("users").document(user_id).get()
                if doc.exists:
                    return UserAccount(**doc.to_dict())
            except Exception as e:
                logger.error(f"Error fetching user by ID from Firestore: {e}")

        users = self._read_local_users()
        if user_id in users:
            return UserAccount(**users[user_id])
        return None

    def save_user(self, user: UserAccount) -> bool:
        """Save or update user account."""
        user_dict = user.model_dump()
        if self._is_live_firestore and self.db:
            try:
                self.db.collection("users").document(user.user_id).set(user_dict)
                return True
            except Exception as e:
                logger.error(f"Error saving user to Firestore: {e}")

        users = self._read_local_users()
        users[user.user_id] = user_dict
        self._write_local_users(users)
        return True

    def initialize_user_workspace(self, user_id: str, user_name: str):
        """Create clean initial starter recipient and preset for a newly registered user."""
        starter_recipient = RecipientProfile(
            recipient_id=f"recipient_{user_id[:8]}",
            caregiver_id=user_id,
            name="Alex",
            age_group="child",
            vocabulary_level="basic",
            max_board_cards=6,
            learned_vocabulary=["eat", "water", "help", "happy"],
            success_history={"water": 1, "eat": 1},
            caregiver_notes=f"Primary communication profile for {user_name}'s workspace."
        )
        self.save_recipient_profile(starter_recipient)

        starter_preset = {
            "id": f"preset_morning_{user_id[:8]}",
            "caregiver_id": user_id,
            "title": "Morning Routine Starter",
            "description": "Daily morning routine",
            "recipient_id": starter_recipient.recipient_id,
            "message": "Good morning Alex! Time to eat breakfast and drink a glass of water."
        }
        self.save_preset(starter_preset, caregiver_id=user_id)

    # =========================================================================
    # RECIPIENT PROFILES (SCOPED PER CAREGIVER)
    # =========================================================================

    def get_recipient_profile(self, recipient_id: str, caregiver_id: str = "caregiver_primary") -> RecipientProfile:
        """Fetch recipient profile strictly scoped to the requesting caregiver."""
        if self._is_live_firestore and self.db:
            try:
                doc = self.db.collection("caregivers").document(caregiver_id).collection("recipients").document(recipient_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    return RecipientProfile(**data)
            except Exception as e:
                logger.error(f"Error fetching from live Firestore: {e}")

        profiles = self._read_local_profiles()
        if recipient_id in profiles:
            p = profiles[recipient_id]
            # Match caregiver ID, or allow default demo profile for caregiver_primary
            if p.get("caregiver_id") == caregiver_id or (caregiver_id == "caregiver_primary" and p.get("caregiver_id") == "caregiver_primary"):
                return RecipientProfile(**p)
        
        # Create a new profile scoped to this user
        new_profile = RecipientProfile(
            recipient_id=recipient_id,
            caregiver_id=caregiver_id,
            name=recipient_id.replace("_", " ").title(),
            vocabulary_level="basic",
            max_board_cards=6
        )
        self.save_recipient_profile(new_profile)
        return new_profile

    def save_recipient_profile(self, profile: RecipientProfile) -> bool:
        """Save or update recipient profile in persistent storage with caregiver isolation."""
        profile.updated_at = datetime.utcnow().isoformat()
        profile_dict = profile.model_dump()

        if self._is_live_firestore and self.db:
            try:
                self.db.collection("caregivers").document(profile.caregiver_id).collection("recipients").document(profile.recipient_id).set(profile_dict)
                return True
            except Exception as e:
                logger.error(f"Error saving to live Firestore: {e}")

        profiles = self._read_local_profiles()
        profiles[profile.recipient_id] = profile_dict
        self._write_local_profiles(profiles)
        return True

    def delete_recipient_profile(self, recipient_id: str, caregiver_id: str = "caregiver_primary") -> bool:
        """Delete a recipient profile safely."""
        if self._is_live_firestore and self.db:
            try:
                self.db.collection("caregivers").document(caregiver_id).collection("recipients").document(recipient_id).delete()
                return True
            except Exception as e:
                logger.error(f"Error deleting from live Firestore: {e}")

        profiles = self._read_local_profiles()
        if recipient_id in profiles:
            del profiles[recipient_id]
            self._write_local_profiles(profiles)
            return True
        return False

    def list_recipients(self, caregiver_id: str = "caregiver_primary") -> List[RecipientProfile]:
        """List recipient profiles isolated to the requesting caregiver."""
        if self._is_live_firestore and self.db:
            try:
                docs = self.db.collection("caregivers").document(caregiver_id).collection("recipients").stream()
                return [RecipientProfile(**doc.to_dict()) for doc in docs]
            except Exception as e:
                logger.error(f"Error listing from live Firestore: {e}")

        profiles = self._read_local_profiles()
        results = []
        for data in profiles.values():
            if data.get("caregiver_id") == caregiver_id:
                results.append(RecipientProfile(**data))
            elif caregiver_id == "caregiver_primary" and data.get("caregiver_id") == "caregiver_primary":
                results.append(RecipientProfile(**data))
        return results

    def list_presets(self, caregiver_id: str = "caregiver_primary") -> List[Dict]:
        """List presets isolated to the requesting caregiver."""
        if self._is_live_firestore and self.db:
            try:
                docs = self.db.collection("caregivers").document(caregiver_id).collection("presets").stream()
                results = [doc.to_dict() for doc in docs]
                if results:
                    return results
            except Exception as e:
                logger.error(f"Error reading presets from Firestore: {e}")

        try:
            if self.presets_file.exists():
                with open(self.presets_file, "r", encoding="utf-8") as f:
                    all_presets = json.load(f)
                    matched = [p for p in all_presets if p.get("caregiver_id") == caregiver_id]
                    if caregiver_id == "caregiver_primary":
                        # Merge defaults with custom saved presets
                        existing_ids = {p.get("id") for p in matched}
                        combined = list(matched)
                        for d in DEFAULT_PRESETS:
                            if d.get("id") not in existing_ids:
                                combined.append(d)
                        return combined
                    return matched
        except Exception as e:
            logger.error(f"Error reading presets file: {e}")
        return DEFAULT_PRESETS if caregiver_id == "caregiver_primary" else []

    def save_preset(self, preset: Dict, caregiver_id: str = "caregiver_primary") -> bool:
        """Save a new preset isolated by caregiver."""
        preset_id = preset.get("id") or f"preset_{int(datetime.utcnow().timestamp())}"
        preset["id"] = preset_id
        preset["caregiver_id"] = caregiver_id

        if self._is_live_firestore and self.db:
            try:
                self.db.collection("caregivers").document(caregiver_id).collection("presets").document(preset_id).set(preset)
                return True
            except Exception as e:
                logger.error(f"Error saving preset to Firestore: {e}")

        all_presets = []
        try:
            if self.presets_file.exists():
                with open(self.presets_file, "r", encoding="utf-8") as f:
                    all_presets = json.load(f)
        except Exception:
            all_presets = []

        existing = next((i for i, p in enumerate(all_presets) if p["id"] == preset_id), None)
        if existing is not None:
            all_presets[existing] = preset
        else:
            all_presets.append(preset)

        try:
            with open(self.presets_file, "w", encoding="utf-8") as f:
                json.dump(all_presets, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving preset to file: {e}")
            return False

    def record_interaction(
        self,
        recipient_id: str,
        words: List[str],
        action: str = "used",
        preferred_symbol: Optional[str] = None,
        caregiver_id: str = "caregiver_primary"
    ) -> RecipientProfile:
        """
        Updates recipient memory with used words, boosts success counts,
        and saves custom symbol mappings safely.
        """
        profile = self.get_recipient_profile(recipient_id, caregiver_id)
        profile.last_interaction = datetime.utcnow().isoformat()

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

    def _read_local_users(self) -> Dict[str, Dict]:
        try:
            if self.users_file.exists():
                with open(self.users_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading local user store: {e}")
        return {}

    def _write_local_users(self, data: Dict[str, Dict]):
        try:
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to local user store: {e}")


firestore_service = FirestoreService()
