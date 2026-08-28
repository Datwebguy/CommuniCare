"""
AAC Symbol Library and Resolver.
Provides open-license AAC pictograms (dynamic ARASAAC API querying + premium vector illustrations)
with Fitzgerald Key color coding and graceful text-card fallback.
"""

import re
import logging
import requests
from typing import Dict, List, Optional, Tuple
from communicare.models import GrammarCategory, SymbolCard, SymbolSource

logger = logging.getLogger("communicare.symbols")

# Fitzgerald Key clinical AAC color palette: (Border/Accent color, Soft Background color, Text color)
FITZGERALD_PALETTE: Dict[GrammarCategory, Tuple[str, str, str]] = {
    GrammarCategory.PEOPLE: ("#EAB308", "#FEFCE8", "#854D0E"),          # Yellow: People / Pronouns
    GrammarCategory.VERB: ("#10B981", "#ECFDF5", "#065F46"),            # Green: Verbs / Actions
    GrammarCategory.NOUN: ("#F97316", "#FFF7ED", "#9A3412"),            # Orange: Nouns / Objects / Food
    GrammarCategory.ADJECTIVE: ("#3B82F6", "#EFF6FF", "#1E40AF"),       # Blue: Adjectives / Descriptors
    GrammarCategory.SOCIAL_FEELINGS: ("#EC4899", "#FDF2F8", "#9D174D"), # Pink: Social words / Feelings
    GrammarCategory.TIME_SCHEDULE: ("#8B5CF6", "#F5F3FF", "#5B21B6"),   # Purple: Time / Routines / Sequence
    GrammarCategory.MISC: ("#64748B", "#F8FAFC", "#334155"),            # Slate: Prepositions / Misc
}

# Premium, Friendly, High-Contrast Vector AAC Pictograms (Curated High-Frequency Tokens)
SVG_ICONS: Dict[str, str] = {
    "medicine": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="22" y="24" width="36" height="46" rx="8" fill="#FEE2E2" stroke="#DC2626" stroke-width="3"/>
      <rect x="28" y="12" width="24" height="12" rx="4" fill="#E2E8F0" stroke="#64748B" stroke-width="3"/>
      <rect x="36" y="34" width="8" height="24" rx="2" fill="#EF4444"/>
      <rect x="28" y="42" width="24" height="8" rx="2" fill="#EF4444"/>
      <circle cx="56" cy="28" r="8" fill="#FBBF24" stroke="#D97706" stroke-width="2.5"/>
      <line x1="56" y1="23" x2="56" y2="33" stroke="#92400E" stroke-width="2" stroke-linecap="round"/>
    </svg>''',
    
    "water": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 18L28 66C28.5 70 32 72 36 72H44C48 72 51.5 70 52 66L58 18H22Z" fill="#E0F2FE" stroke="#0284C7" stroke-width="3"/>
      <path d="M25 38C30 35 34 40 40 38C46 36 50 40 55 38L57 26H23L25 38Z" fill="#38BDF8" opacity="0.85"/>
      <path d="M38 12C38 12 34 22 40 22C46 22 42 12 42 12" stroke="#0284C7" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "pancakes": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="40" cy="58" rx="28" ry="10" fill="#FDE68A" stroke="#D97706" stroke-width="3"/>
      <ellipse cx="40" cy="46" rx="26" ry="9" fill="#FCD34D" stroke="#D97706" stroke-width="3"/>
      <ellipse cx="40" cy="34" rx="24" ry="8" fill="#FBBF24" stroke="#D97706" stroke-width="3"/>
      <rect x="34" y="20" width="12" height="8" rx="2" fill="#F59E0B" stroke="#B45309" stroke-width="2"/>
      <path d="M38 28C38 34 32 36 32 44" stroke="#D97706" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "breakfast": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="44" r="28" fill="#FFFBEB" stroke="#F59E0B" stroke-width="3.5"/>
      <ellipse cx="40" cy="44" rx="18" ry="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2.5"/>
      <circle cx="40" cy="44" r="9" fill="#F59E0B"/>
      <path d="M14 16V32M10 20H18" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>
      <path d="M66 16V32M62 20C62 26 66 26 66 26" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "eggs": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="40" cy="42" rx="26" ry="20" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="3.5"/>
      <circle cx="38" cy="40" r="11" fill="#F59E0B"/>
      <circle cx="35" cy="37" r="3" fill="#FEF08A"/>
    </svg>''',

    "walk": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="42" cy="18" r="8" fill="#10B981" stroke="#047857" stroke-width="2.5"/>
      <path d="M38 28L32 44L44 48L52 68" stroke="#047857" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M32 44L22 52L16 68" stroke="#047857" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M30 34L44 38L54 32" stroke="#047857" stroke-width="4.5" stroke-linecap="round"/>
      <path d="M12 72H68" stroke="#94A3B8" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "park": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="24" y="44" width="8" height="24" rx="2" fill="#78350F"/>
      <circle cx="28" cy="34" r="18" fill="#86EFAC" stroke="#15803D" stroke-width="3"/>
      <rect x="48" y="40" width="8" height="28" rx="2" fill="#78350F"/>
      <circle cx="52" cy="30" r="20" fill="#4ADE80" stroke="#15803D" stroke-width="3"/>
      <path d="M8 68H72" stroke="#16A34A" stroke-width="4" stroke-linecap="round"/>
      <circle cx="62" cy="14" r="6" fill="#FDE047"/>
    </svg>''',

    "dog": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="42" r="22" fill="#FED7AA" stroke="#EA580C" stroke-width="3"/>
      <ellipse cx="20" cy="32" rx="6" ry="12" fill="#FB923C" stroke="#EA580C" stroke-width="2.5"/>
      <ellipse cx="60" cy="32" rx="6" ry="12" fill="#FB923C" stroke="#EA580C" stroke-width="2.5"/>
      <circle cx="32" cy="38" r="4" fill="#1E293B"/>
      <circle cx="48" cy="38" r="4" fill="#1E293B"/>
      <ellipse cx="40" cy="48" rx="6" ry="4" fill="#1E293B"/>
      <path d="M40 52V56M36 56C38 58 42 58 44 56" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round"/>
    </svg>''',

    "morning": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 56H68" stroke="#7C3AED" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M22 56C22 44 30 34 40 34C50 34 58 44 58 56H22Z" fill="#FDE047" stroke="#EAB308" stroke-width="3"/>
      <line x1="40" y1="16" x2="40" y2="26" stroke="#F59E0B" stroke-width="3.5" stroke-linecap="round"/>
      <line x1="20" y1="24" x2="26" y2="30" stroke="#F59E0B" stroke-width="3.5" stroke-linecap="round"/>
      <line x1="60" y1="24" x2="54" y2="30" stroke="#F59E0B" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M24 64H56" stroke="#8B5CF6" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "doctor": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="24" r="12" fill="#FEF08A" stroke="#CA8A04" stroke-width="3"/>
      <path d="M20 66C20 52 28 44 40 44C52 44 60 52 60 66H20Z" fill="#E0F2FE" stroke="#0284C7" stroke-width="3.5"/>
      <rect x="37" y="50" width="6" height="14" rx="1" fill="#DC2626"/>
      <rect x="33" y="54" width="14" height="6" rx="1" fill="#DC2626"/>
      <path d="M28 24C28 14 52 14 52 24" stroke="#0284C7" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "happy": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#FCE7F3" stroke="#DB2777" stroke-width="3.5"/>
      <circle cx="30" cy="34" r="4" fill="#831843"/>
      <circle cx="50" cy="34" r="4" fill="#831843"/>
      <path d="M26 46C30 56 50 56 54 46" stroke="#DB2777" stroke-width="4.5" stroke-linecap="round"/>
    </svg>''',

    "hurt": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#FEE2E2" stroke="#DC2626" stroke-width="3.5"/>
      <path d="M26 30L34 36M46 36L54 30" stroke="#991B1B" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M28 52C34 46 46 46 52 52" stroke="#DC2626" stroke-width="4.5" stroke-linecap="round"/>
      <path d="M38 12L34 6M42 12L46 6" stroke="#DC2626" stroke-width="3" stroke-linecap="round"/>
    </svg>''',

    "sleep": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="14" y="42" width="52" height="22" rx="4" fill="#EDE9FE" stroke="#7C3AED" stroke-width="3.5"/>
      <rect x="18" y="32" width="16" height="12" rx="3" fill="#FFFFFF" stroke="#A78BFA" stroke-width="2.5"/>
      <circle cx="26" cy="38" r="4" fill="#C4B5FD"/>
      <path d="M48 18L58 14L48 24H58" stroke="#8B5CF6" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M40 26L48 23L40 31H48" stroke="#A78BFA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>''',
}


# Common clinical & vocabulary synonyms mapping to curated vector assets
COMMON_SYNONYMS: Dict[str, str] = {
    "pills": "medicine",
    "pill": "medicine",
    "tablets": "medicine",
    "tablet": "medicine",
    "meds": "medicine",
    "medication": "medicine",
    "puppy": "dog",
    "doggie": "dog",
    "hound": "dog",
    "stroll": "walk",
    "walking": "walk",
    "physician": "doctor",
    "md": "doctor",
    "eating": "breakfast",
    "meal": "breakfast",
    "pancake": "pancakes",
    "egg": "eggs",
    "rest": "sleep",
    "sleeping": "sleep",
    "bed": "sleep",
    "pain": "hurt",
    "ache": "hurt",
    "joy": "happy",
    "glad": "happy",
    "water_glass": "water",
    "drink": "water",
    "drinking": "water",
}


def normalize_term(term: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s_]", "", term.lower().strip())
    return cleaned.replace(" ", "_")


class SymbolResolver:
    """
    Dynamically resolves simplified AAC concepts to high-contrast picture symbols,
    live ARASAAC API pictograms, or graceful text-card fallbacks.
    """

    def __init__(self):
        self.svg_icons = SVG_ICONS
        self.synonyms = COMMON_SYNONYMS
        self.palette = FITZGERALD_PALETTE
        # Dynamic in-memory and network cache for ARASAAC lookups
        self._arasaac_cache: Dict[str, Optional[int]] = {}

    def resolve_concept(
        self,
        concept: str,
        category_hint: Optional[str] = None,
        preferred_symbol_id: Optional[str] = None
    ) -> SymbolCard:
        """
        Dynamically resolves any English concept into a complete SymbolCard.
        """
        norm_concept = normalize_term(concept)

        # 1. Check local high-contrast vector library (direct or synonym)
        target_key = norm_concept if norm_concept in self.svg_icons else self.synonyms.get(norm_concept)
        if target_key and target_key in self.svg_icons:
            category = self._infer_category(concept, category_hint)
            color_code, bg_color, _ = self.palette[category]
            svg_icon = self.svg_icons[target_key]

            return SymbolCard(
                id=f"sym_{norm_concept}",
                word=concept.upper(),
                category=category,
                color_code=color_code,
                bg_color=bg_color,
                image_url=None,
                svg_icon=svg_icon,
                arasaac_id=None,
                source=SymbolSource.CURATED_AAC,
                confidence=1.0,
                is_fallback=False,
                pronunciation_hint=concept.title()
            )

        # 2. Dynamic Live ARASAAC REST API Query
        arasaac_id = self._fetch_arasaac_id(norm_concept)
        if arasaac_id:
            category = self._infer_category(concept, category_hint)
            color_code, bg_color, _ = self.palette[category]
            image_url = f"https://static.arasaac.org/pictograms/{arasaac_id}/{arasaac_id}_500.png"

            return SymbolCard(
                id=f"arasaac_{arasaac_id}",
                word=concept.upper(),
                category=category,
                color_code=color_code,
                bg_color=bg_color,
                image_url=image_url,
                svg_icon=None,
                arasaac_id=arasaac_id,
                source=SymbolSource.ARASAAC,
                confidence=0.95,
                is_fallback=False,
                pronunciation_hint=concept.title()
            )

        # 3. Graceful Accessible Text Fallback Card
        category = self._infer_category(concept, category_hint)
        color_code, bg_color, _ = self.palette[category]

        return SymbolCard(
            id=f"card_{norm_concept}",
            word=concept.upper(),
            category=category,
            color_code=color_code,
            bg_color=bg_color,
            image_url=None,
            svg_icon=None,
            arasaac_id=None,
            source=SymbolSource.TEXT_FALLBACK,
            confidence=0.5,
            is_fallback=True,
            pronunciation_hint=concept.title(),
            subtext="Text Card"
        )

    def _fetch_arasaac_id(self, term: str) -> Optional[int]:
        """
        Dynamically search the open ARASAAC REST API for any English term.
        """
        clean_word = term.replace("_", " ").strip()
        if clean_word in self._arasaac_cache:
            return self._arasaac_cache[clean_word]

        try:
            url = f"https://api.arasaac.org/api/pictograms/en/search/{clean_word}"
            resp = requests.get(url, timeout=3.0)
            if resp.status_code == 200:
                results = resp.json()
                if results and isinstance(results, list) and len(results) > 0:
                    picto_id = results[0].get("_id")
                    if picto_id:
                        self._arasaac_cache[clean_word] = picto_id
                        return picto_id
        except Exception as e:
            logger.debug(f"ARASAAC live API query for '{clean_word}' skipped: {e}")

        self._arasaac_cache[clean_word] = None
        return None

    def _infer_category(self, concept: str, category_hint: Optional[str]) -> GrammarCategory:
        if category_hint:
            try:
                return GrammarCategory(category_hint.lower())
            except ValueError:
                pass

        lower = concept.lower()
        if lower in ["i", "you", "we", "he", "she", "mom", "dad", "doctor", "nurse", "friend", "teacher", "me", "caregiver"]:
            return GrammarCategory.PEOPLE
        if lower in ["eat", "drink", "walk", "go", "stop", "help", "take", "sleep", "wash", "play", "see", "want", "like", "listen", "read"]:
            return GrammarCategory.VERB
        if lower in ["happy", "sad", "hurt", "tired", "good", "bad", "calm", "please", "thanks", "yes", "no", "more", "all done"]:
            return GrammarCategory.SOCIAL_FEELINGS
        if lower in ["now", "later", "morning", "afternoon", "night", "today", "tomorrow", "first", "then", "time"]:
            return GrammarCategory.TIME_SCHEDULE
        if lower in ["big", "small", "hot", "cold", "fast", "slow", "red", "blue", "quiet"]:
            return GrammarCategory.ADJECTIVE
        return GrammarCategory.NOUN

    def search_symbols(self, query: str, limit: int = 10) -> List[Dict]:
        """Dynamically search available symbols via live API and local set."""
        q = normalize_term(query)
        results = []

        # Local vector matches
        for key in self.svg_icons:
            if q in key:
                results.append({
                    "id": key,
                    "word": key.title(),
                    "category": self._infer_category(key, None).value,
                    "source": "curated_vector"
                })

        # ARASAAC live API search
        try:
            url = f"https://api.arasaac.org/api/pictograms/en/search/{q}"
            resp = requests.get(url, timeout=3.0)
            if resp.status_code == 200:
                api_results = resp.json()
                for item in api_results[:limit]:
                    results.append({
                        "id": str(item.get("_id")),
                        "word": item.get("keywords", [{}])[0].get("keyword", q).title() if item.get("keywords") else q.title(),
                        "category": "noun",
                        "arasaac_id": item.get("_id"),
                        "image_url": f"https://static.arasaac.org/pictograms/{item.get('_id')}/{item.get('_id')}_500.png",
                        "source": "arasaac_api"
                    })
        except Exception as e:
            logger.debug(f"Search API error: {e}")

        return results[:limit]


symbol_resolver = SymbolResolver()
