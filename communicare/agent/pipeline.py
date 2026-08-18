"""
Autonomous Agent Pipeline for CommuniCare (Taskmaster Track).
Orchestrates end-to-end message simplification, memory retrieval, symbol reasoning,
board assembly, and persistent state updates.
"""

import time
import uuid
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

from communicare.models import (
    CaregiverMessageRequest,
    AACBoardResponse,
    RecipientProfile,
    SymbolCard,
    PipelineStepTrace,
    GrammarCategory
)
from communicare.services.gemini_service import gemini_service
from communicare.services.symbol_library import symbol_resolver
from communicare.services.firestore_service import firestore_service

logger = logging.getLogger("communicare.agent")


class CommuniCareAgent:
    """
    Taskmaster Autonomous Agent that takes a complex caregiver message
    and produces an accessible, high-contrast AAC picture symbol board.
    """

    def __init__(self):
        self.gemini = gemini_service
        self.symbol_resolver = symbol_resolver
        self.firestore = firestore_service

    def process_caregiver_message(self, request: CaregiverMessageRequest) -> AACBoardResponse:
        """
        Executes the autonomous 5-step Taskmaster agent pipeline:
        1. Context & Profile Retrieval (Firestore)
        2. Natural Language Simplification & Concept Extraction (Gemini 2.5/3.5 Flash)
        3. Symbol Resolution & Preference Alignment (ARASAAC / AAC Library)
        4. High-Contrast Board Assembly & Fitzgerald Key Categorization
        5. Memory Update & Interaction Logging (Firestore)
        """
        board_id = f"board_{uuid.uuid4().hex[:8]}"
        trace: List[PipelineStepTrace] = []
        adaptations: List[str] = []

        # =========================================================================
        # STEP 1: Recipient Profile & State Retrieval
        # =========================================================================
        t0 = time.perf_counter()
        profile: RecipientProfile = self.firestore.get_recipient_profile(request.recipient_id)
        duration_step1 = (time.perf_counter() - t0) * 1000

        trace.append(PipelineStepTrace(
            step_number=1,
            step_name="Profile & Memory Lookup",
            description=f"Retrieved persistent profile for {profile.name} from Firestore",
            status="completed",
            input_summary=f"Recipient ID: {request.recipient_id}",
            output_summary=f"Vocab Level: {profile.vocabulary_level}, Known Words: {len(profile.learned_vocabulary)}, Preferred Mappings: {len(profile.preferred_symbol_mappings)}",
            reasoning=f"Care recipient prefers maximum {profile.max_board_cards} cards. Notes: '{profile.caregiver_notes or 'None'}'",
            duration_ms=round(duration_step1, 2)
        ))

        # =========================================================================
        # STEP 2: Gemini Language Simplification & Reasoning
        # =========================================================================
        t1 = time.perf_counter()
        simplification = self.gemini.simplify_and_extract_concepts(
            raw_message=request.message,
            profile=profile,
            style=request.simplify_style or "core_words"
        )
        duration_step2 = (time.perf_counter() - t1) * 1000

        trace.append(PipelineStepTrace(
            step_number=2,
            step_name="Gemini Language Simplification",
            description="Gemini simplified the raw message into core AAC concepts",
            status="completed",
            input_summary=f"Raw: '{request.message}'",
            output_summary=f"Extracted {len(simplification.concepts)} concepts: {', '.join(c.concept for c in simplification.concepts)}",
            reasoning=simplification.gemini_reasoning,
            duration_ms=round(duration_step2, 2)
        ))

        # =========================================================================
        # STEP 3: Symbol Resolution & Disambiguation
        # =========================================================================
        t2 = time.perf_counter()
        resolved_cards: List[SymbolCard] = []
        words_for_memory: List[str] = []

        for concept_item in simplification.concepts:
            concept_name = concept_item.concept
            category_hint = concept_item.category
            words_for_memory.append(concept_name)

            # Check if care recipient has a personalized symbol preference
            preferred_symbol = profile.preferred_symbol_mappings.get(concept_name.lower())
            if preferred_symbol:
                adaptations.append(f"Applied personalized symbol preference for '{concept_name}'")

            card = self.symbol_resolver.resolve_concept(
                concept=concept_name,
                category_hint=category_hint,
                preferred_symbol_id=preferred_symbol
            )
            resolved_cards.append(card)

        duration_step3 = (time.perf_counter() - t2) * 1000

        fallback_count = sum(1 for c in resolved_cards if c.is_fallback)
        trace.append(PipelineStepTrace(
            step_number=3,
            step_name="AAC Symbol Resolution",
            description="Resolved concepts against ARASAAC open library and curated vector icons",
            status="fallback" if fallback_count > 0 else "completed",
            input_summary=f"Resolving {len(simplification.concepts)} concepts",
            output_summary=f"{len(resolved_cards) - fallback_count} visual symbols resolved, {fallback_count} graceful text fallbacks",
            reasoning="Applied open-license ARASAAC mappings and local high-contrast SVGs. Fallback activated for uncatalogued terms.",
            duration_ms=round(duration_step3, 2)
        ))

        # =========================================================================
        # STEP 4: High-Contrast Board Layout & Color Composition
        # =========================================================================
        t3 = time.perf_counter()
        # Sort cards into logical AAC Fitzgerald sequence:
        # Time -> People -> Verbs -> Nouns -> Social/Feelings
        CATEGORY_ORDER = {
            GrammarCategory.TIME_SCHEDULE: 1,
            GrammarCategory.PEOPLE: 2,
            GrammarCategory.VERB: 3,
            GrammarCategory.NOUN: 4,
            GrammarCategory.ADJECTIVE: 5,
            GrammarCategory.SOCIAL_FEELINGS: 6,
            GrammarCategory.MISC: 7
        }
        resolved_cards.sort(key=lambda c: CATEGORY_ORDER.get(c.category, 99))
        duration_step4 = (time.perf_counter() - t3) * 1000

        trace.append(PipelineStepTrace(
            step_number=4,
            step_name="Board Layout & Fitzgerald Composition",
            description="Assembled high-contrast grid with AAC color coding and audio hints",
            status="completed",
            input_summary=f"{len(resolved_cards)} cards",
            output_summary=f"Structured {len(resolved_cards)}-card AAC board ready for recipient",
            reasoning="Arranged cards by clinical Fitzgerald Key order for maximum cognitive clarity.",
            duration_ms=round(duration_step4, 2)
        ))

        # =========================================================================
        # STEP 5: State Persistence & Profile Learning
        # =========================================================================
        t4 = time.perf_counter()
        self.firestore.record_interaction(
            recipient_id=profile.recipient_id,
            words=words_for_memory,
            action="used"
        )
        duration_step5 = (time.perf_counter() - t4) * 1000

        trace.append(PipelineStepTrace(
            step_number=5,
            step_name="Memory State Update",
            description="Updated recipient vocabulary history and usage stats in Firestore",
            status="completed",
            input_summary=f"Words: {', '.join(words_for_memory)}",
            output_summary="Saved to Firestore recipient document",
            reasoning="Allows the agent to personalize future boards based on successful vocabulary.",
            duration_ms=round(duration_step5, 2)
        ))

        return AACBoardResponse(
            board_id=board_id,
            recipient_id=profile.recipient_id,
            recipient_name=profile.name,
            original_message=request.message,
            simplified_message=simplification.simplified_message,
            core_intent=simplification.core_intent,
            cards=resolved_cards,
            pipeline_trace=trace,
            personalized_adaptations_applied=adaptations,
            created_at=datetime.utcnow().isoformat()
        )


# Singleton agent instance
agent_orchestrator = CommuniCareAgent()
