"""
Data models and schemas for CommuniCare.
Defines AAC symbols, recipient profiles, pipeline trace, and API contracts.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GrammarCategory(str, Enum):
    """
    Fitzgerald Key AAC Color Coding Standard:
    - PEOPLE: Yellow (#FFD700 / #FEF08A)
    - VERB: Green (#22C55E / #BBF7D0)
    - NOUN: Orange (#F97316 / #FFEDD5)
    - ADJECTIVE: Blue (#3B82F6 / #BFDBFE)
    - SOCIAL_FEELINGS: Pink (#EC4899 / #FBCFE8)
    - TIME_SCHEDULE: Purple (#8B5CF6 / #DDD6FE)
    - MISC: Slate (#64748B / #E2E8F0)
    """
    PEOPLE = "people"
    VERB = "verb"
    NOUN = "noun"
    ADJECTIVE = "adjective"
    SOCIAL_FEELINGS = "social_feelings"
    TIME_SCHEDULE = "time_schedule"
    MISC = "misc"


class SymbolSource(str, Enum):
    ARASAAC = "arasaac"
    CURATED_AAC = "curated_aac"
    TEXT_FALLBACK = "text_fallback"


class SymbolCard(BaseModel):
    id: str
    word: str
    category: GrammarCategory = GrammarCategory.NOUN
    color_code: str = "#F97316"
    bg_color: str = "#FFF7ED"
    image_url: Optional[str] = None
    svg_icon: Optional[str] = None
    arasaac_id: Optional[int] = None
    source: SymbolSource = SymbolSource.CURATED_AAC
    confidence: float = 1.0
    is_fallback: bool = False
    pronunciation_hint: Optional[str] = None
    subtext: Optional[str] = None


class RecipientProfile(BaseModel):
    recipient_id: str
    name: str
    age_group: str = "child"  # "child", "teen", "adult"
    vocabulary_level: str = "basic"  # "basic" (1-4 words), "intermediate" (4-6 words), "advanced" (6-8 words)
    max_board_cards: int = 6
    high_contrast_mode: bool = True
    color_coding_enabled: bool = True
    preferred_symbol_mappings: Dict[str, str] = Field(default_factory=dict)
    learned_vocabulary: List[str] = Field(default_factory=list)
    success_history: Dict[str, int] = Field(default_factory=dict)
    caregiver_notes: Optional[str] = None
    last_interaction: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PipelineStepTrace(BaseModel):
    step_number: int
    step_name: str
    description: str
    status: str = "completed"  # "started", "completed", "fallback", "skipped"
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    reasoning: Optional[str] = None
    duration_ms: float = 0.0


class CaregiverMessageRequest(BaseModel):
    message: str = Field(..., description="Raw natural language caregiver message or care note")
    recipient_id: str = Field(default="alex_care", description="Identifier of the care recipient")
    simplify_style: Optional[str] = Field(default="core_words", description="Simplification style: core_words, step_by_step, or routine")
    custom_notes: Optional[str] = None


class AACBoardResponse(BaseModel):
    board_id: str
    recipient_id: str
    recipient_name: str
    original_message: str
    simplified_message: str
    core_intent: str
    cards: List[SymbolCard]
    pipeline_trace: List[PipelineStepTrace]
    personalized_adaptations_applied: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class FeedbackRequest(BaseModel):
    board_id: str
    recipient_id: str
    card_id: Optional[str] = None
    word: Optional[str] = None
    action: str = Field(..., description="'worked_well', 'replace_symbol', 'add_preference', 'mark_difficult'")
    preferred_symbol: Optional[str] = None
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str
    recipient_id: str
    updated_memory_summary: Dict[str, Any]
