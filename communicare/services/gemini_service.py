"""
Gemini Reasoning & Language Simplification Service for CommuniCare.
Uses Google GenAI SDK to simplify caregiver messages and map concepts to AAC tokens.
Includes robust natural-language heuristic engine for offline development and testing.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from communicare.models import RecipientProfile, GrammarCategory

load_dotenv()

logger = logging.getLogger("communicare.gemini")


class ExtractedConcept(BaseModel):
    concept: str
    category: str = "noun"
    priority: int = 5
    reasoning: str = ""


class SimplificationResult(BaseModel):
    simplified_message: str
    core_intent: str
    concepts: List[ExtractedConcept]
    gemini_reasoning: str


class GeminiService:
    """
    Interfaces with Google Gemini (via google-genai SDK) to perform:
    1. Plain language simplification for AAC users.
    2. Concept extraction and grammatical classification.
    3. Integration of recipient's memory profile.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Google GenAI client with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client ({e}). Heuristic engine active.")
        else:
            logger.info("No live GEMINI_API_KEY provided. Operating with built-in heuristic reasoning engine.")

    def simplify_and_extract_concepts(
        self,
        raw_message: str,
        profile: RecipientProfile,
        style: str = "core_words"
    ) -> SimplificationResult:
        """
        Main reasoning step: Transforms raw caregiver input into simplified AAC concepts,
        informed by the care recipient's profile and memory.
        """
        # If live Gemini client is available, call Gemini API
        if self.client:
            try:
                return self._call_gemini_api(raw_message, profile, style)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to heuristic reasoning engine.")

        # Fallback heuristic engine
        return self._heuristic_simplification(raw_message, profile, style)

    def _call_gemini_api(
        self,
        raw_message: str,
        profile: RecipientProfile,
        style: str
    ) -> SimplificationResult:
        """Call Google GenAI SDK with structured JSON prompt."""
        from google.genai import types

        prompt = f"""
You are the CommuniCare AAC Agent, an expert in Augmentative and Alternative Communication for nonverbal and speech-limited individuals.

Your task is to transform this raw caregiver message into a clean, simple AAC communication board:
CAREGIVER MESSAGE: "{raw_message}"

CARE RECIPIENT PROFILE:
- Name: {profile.name} (Age group: {profile.age_group})
- Vocabulary Level: {profile.vocabulary_level} (Max cards: {profile.max_board_cards})
- Known Vocabulary: {', '.join(profile.learned_vocabulary[:15])}
- Preferred Symbol Mappings: {json.dumps(profile.preferred_symbol_mappings)}
- Caregiver Notes: {profile.caregiver_notes or 'None'}

INSTRUCTIONS:
1. Simplify the message into a short, natural, complete plain language sentence (1-2 sentences max, easy for text-to-speech to read aloud smoothly). Never use arrows (→), bullet symbols, or metadata labels in the simplified sentence.
2. Extract {profile.max_board_cards} essential concepts/words that convey the action, key items, and emotions.
3. Categorize each concept using Fitzgerald Key grammar:
   - "people" (Yellow): I, you, doctor, caregiver, friend
   - "verb" (Green): eat, drink, walk, take, help, sleep, wash, play
   - "noun" (Orange): medicine, water, pancakes, eggs, park, dog, bathroom, bed, shoes
   - "adjective" (Blue): big, small, hot, cold, quiet
   - "social_feelings" (Pink): happy, hurt, tired, yes, no, calm, more, all done
   - "time_schedule" (Purple): now, later, morning, afternoon
   - "misc" (Slate): miscellaneous
4. Prioritize words the recipient already knows or prefers.

Respond ONLY with valid JSON matching this schema:
{{
  "simplified_message": "A clean, natural plain language sentence to speak aloud",
  "core_intent": "Brief 2-4 word intent summary",
  "gemini_reasoning": "string explaining how the message was simplified and adapted to the profile",
  "concepts": [
    {{
      "concept": "word",
      "category": "verb|noun|people|adjective|social_feelings|time_schedule|misc",
      "priority": 10,
      "reasoning": "why this word was chosen"
    }}
  ]
}}
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        raw_json = response.text.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3].strip()
        elif raw_json.startswith("```"):
            raw_json = raw_json[3:-3].strip()

        data = json.loads(raw_json)
        concepts = [ExtractedConcept(**c) for c in data.get("concepts", [])]

        return SimplificationResult(
            simplified_message=data.get("simplified_message", raw_message),
            core_intent=data.get("core_intent", "Communication Support"),
            gemini_reasoning=data.get("gemini_reasoning", "Gemini 3.5 Flash simplified plain language concepts."),
            concepts=concepts[:profile.max_board_cards]
        )

    def _heuristic_simplification(
        self,
        raw_message: str,
        profile: RecipientProfile,
        style: str
    ) -> SimplificationResult:
        """
        Intelligent offline reasoning heuristic for testing and demo reliability.
        Produces complete, natural plain language sentences and extracts salient AAC concepts.
        """
        msg_lower = raw_message.lower()
        extracted: List[ExtractedConcept] = []
        seen = set()

        # Keyword mapping dictionary for offline heuristic
        KEYWORD_RULES = [
            # Time & Sequence
            ("morning", "time_schedule", "Time indicator for morning routine"),
            ("now", "time_schedule", "Immediate action indicator"),
            ("later", "time_schedule", "Sequence and future action"),
            ("afternoon", "time_schedule", "Afternoon time marker"),
            ("evening", "time_schedule", "Evening routine indicator"),
            # Medical / Care
            ("medicine", "noun", "Essential care item"),
            ("pills", "noun", "Medication item"),
            ("doctor", "people", "Medical professional"),
            ("teeth", "noun", "Hygiene care item"),
            ("wash", "verb", "Hygiene action"),
            ("bathroom", "noun", "Daily care location"),
            ("toilet", "noun", "Hygiene requirement"),
            # Nutrition
            ("water", "noun", "Hydration item"),
            ("breakfast", "noun", "Morning meal"),
            ("pancakes", "noun", "Breakfast food item"),
            ("eggs", "noun", "Food item"),
            ("juice", "noun", "Beverage item"),
            ("milk", "noun", "Beverage item"),
            ("eat", "verb", "Nutrition action"),
            ("drink", "verb", "Hydration action"),
            ("snack", "noun", "Food snack item"),
            ("lunch", "noun", "Midday meal"),
            ("dinner", "noun", "Evening meal"),
            # Activities & Locations
            ("walk", "verb", "Physical activity"),
            ("park", "noun", "Outdoor destination"),
            ("dog", "noun", "Companion animal and subject"),
            ("dogs", "noun", "Companion animal and subject"),
            ("car", "noun", "Transportation vehicle"),
            ("bus", "noun", "Transit vehicle"),
            ("school", "noun", "Educational setting"),
            ("play", "verb", "Leisure and recreational activity"),
            ("book", "noun", "Reading activity"),
            ("music", "noun", "Audio sensory engagement"),
            ("sleep", "verb", "Resting state"),
            ("bed", "noun", "Rest location"),
            ("shoes", "noun", "Clothing item for transition"),
            ("coat", "noun", "Clothing item"),
            # Social / Emotional / Sensory
            ("happy", "social_feelings", "Positive emotion"),
            ("hurt", "social_feelings", "Pain or discomfort"),
            ("tired", "social_feelings", "Fatigue indicator"),
            ("quiet", "adjective", "Calm sensory environment"),
            ("calm", "adjective", "Regulation state"),
            ("help", "verb", "Assistance request"),
            ("stop", "verb", "Halt action"),
            ("yes", "social_feelings", "Affirmation"),
            ("no", "social_feelings", "Refusal"),
            ("all done", "social_feelings", "Completion marker"),
            ("more", "social_feelings", "Continuation request"),
        ]

        # 1. Match against recipient preferred mappings first
        for pref_word in profile.preferred_symbol_mappings:
            if pref_word in msg_lower and pref_word not in seen:
                extracted.append(ExtractedConcept(
                    concept=pref_word,
                    category="noun" if pref_word not in ["walk", "eat", "drink", "sleep", "wash"] else "verb",
                    priority=10,
                    reasoning=f"Matched care recipient's preferred vocabulary: '{pref_word}'"
                ))
                seen.add(pref_word)

        # 2. Check rule matches in the message
        for word, category, reasoning in KEYWORD_RULES:
            if word in msg_lower and word not in seen:
                bonus = profile.success_history.get(word, 0)
                extracted.append(ExtractedConcept(
                    concept=word.replace(" ", "_"),
                    category=category,
                    priority=7 + min(bonus, 3),
                    reasoning=reasoning
                ))
                seen.add(word)

        # 3. If extracted is short, extract fallback key tokens
        if len(extracted) < 2:
            words = [w.strip(".,!?:;\"'()[]{}") for w in msg_lower.split()]
            stop_words = {"the", "a", "an", "and", "or", "to", "for", "in", "on", "at", "is", "are", "it", "this", "that", "with", "we", "will", "let", "lets", "please"}
            for w in words:
                if len(w) > 2 and w not in stop_words and w not in seen:
                    extracted.append(ExtractedConcept(
                        concept=w,
                        category="noun",
                        priority=4,
                        reasoning=f"Extracted key term from caregiver message: '{w}'"
                    ))
                    seen.add(w)
                    if len(extracted) >= profile.max_board_cards:
                        break

        # Sort by priority
        extracted.sort(key=lambda c: c.priority, reverse=True)
        final_concepts = extracted[:profile.max_board_cards]

        # Generate a complete, natural plain language sentence (NO arrows or technical codes)
        simplified_sentence = self._synthesize_natural_sentence(raw_message, final_concepts, profile)
        core_intent = self._infer_core_intent(final_concepts, raw_message)

        return SimplificationResult(
            simplified_message=simplified_sentence,
            core_intent=core_intent,
            gemini_reasoning=(
                f"Extracted {len(final_concepts)} high salience concepts tailored to "
                f"{profile.name}'s {profile.vocabulary_level} vocabulary level. "
                f"Prioritized known successful words ({', '.join(k for k in profile.success_history if k in seen) or 'none'})."
            ),
            concepts=final_concepts
        )

    def _synthesize_natural_sentence(
        self,
        raw_message: str,
        concepts: List[ExtractedConcept],
        profile: RecipientProfile
    ) -> str:
        """
        Constructs a complete, grammatical plain-language sentence suitable for speech synthesis.
        Eliminates jargon, arrows, and complex clauses while preserving conversational warmth.
        """
        c_words = {c.concept.lower().replace("_", " ") for c in concepts}
        
        first_name = profile.name.split()[0] if profile.name and "Test" not in profile.name else ""
        greeting = f"Good morning {first_name}. " if "morning" in c_words and first_name else (f"Hello {first_name}. " if first_name else "")

        # Routine patterns
        actions = []
        if "medicine" in c_words or "pills" in c_words:
            if "water" in c_words:
                actions.append("take your medicine with a glass of water")
            else:
                actions.append("take your medicine")
        
        if "pancakes" in c_words:
            actions.append("eat warm pancakes for breakfast")
        elif "breakfast" in c_words or "eggs" in c_words:
            actions.append("eat breakfast")
        elif "snack" in c_words or "lunch" in c_words:
            actions.append("have a healthy snack")

        if "walk" in c_words:
            if "park" in c_words and ("dog" in c_words or "dogs" in c_words):
                actions.append("take a walk to the park to see the dogs")
            elif "park" in c_words:
                actions.append("take a walk to the park")
            else:
                actions.append("go for a walk outside")

        if "doctor" in c_words:
            actions.append("the doctor will visit today to help check your health")

        if "teeth" in c_words or "wash" in c_words:
            actions.append("brush your teeth and wash up")

        if "sleep" in c_words or "bed" in c_words:
            actions.append("time to rest and go to sleep")

        if actions:
            if len(actions) == 1:
                return f"{greeting}Please {actions[0]}."
            elif len(actions) == 2:
                return f"{greeting}Please {actions[0]}, then {actions[1]}."
            else:
                return f"{greeting}First {actions[0]}, then {actions[1]}, and {actions[2]}."

        # If no hardcoded template matched, clean the original caregiver sentence directly
        cleaned = raw_message.strip()
        cleaned = cleaned.replace("→", " ").replace("->", " ").replace("•", " ")
        sentences = [s.strip() for s in cleaned.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if sentences:
            return sentences[0] + "."

        return "Time for our daily routine."

    def _infer_core_intent(self, concepts: List[ExtractedConcept], raw_message: str) -> str:
        """Categorizes the primary clinical or care routine intent."""
        c_names = {c.concept.lower().replace("_", " ") for c in concepts}
        
        if any(w in c_names for w in ["medicine", "pills", "doctor", "hurt"]):
            return "Medical & Care Routine"
        if any(w in c_names for w in ["breakfast", "pancakes", "eggs", "eat", "drink", "water", "snack", "lunch"]):
            return "Meal & Hydration"
        if any(w in c_names for w in ["walk", "park", "dog", "dogs", "play", "car", "bus", "school"]):
            return "Daily Activity & Transition"
        if any(w in c_names for w in ["sleep", "bed", "teeth", "wash", "toilet", "bathroom"]):
            return "Hygiene & Bedtime Routine"
        if any(w in c_names for w in ["happy", "tired", "calm", "quiet", "help"]):
            return "Feelings & Emotional Support"
        return "Daily Communication"


# Singleton instance
gemini_service = GeminiService()
