"""
AAC Symbol Library and Resolver.
Provides open-license AAC pictograms (ARASAAC and curated high-contrast vector symbols)
with Fitzgerald Key color coding and graceful text-card fallback.
"""

import re
from typing import Dict, List, Optional, Tuple
from communicare.models import GrammarCategory, SymbolCard, SymbolSource

# Fitzgerald Key color mappings: (Border/Accent color, Light BG color)
FITZGERALD_PALETTE: Dict[GrammarCategory, Tuple[str, str]] = {
    GrammarCategory.PEOPLE: ("#CA8A04", "#FEF9C3"),         # Yellow: People / Pronouns
    GrammarCategory.VERB: ("#16A34A", "#DCFCE7"),           # Green: Verbs / Actions
    GrammarCategory.NOUN: ("#EA580C", "#FFEDD5"),           # Orange: Nouns / Objects / Food
    GrammarCategory.ADJECTIVE: ("#2563EB", "#DBEAFE"),      # Blue: Adjectives / Descriptors
    GrammarCategory.SOCIAL_FEELINGS: ("#DB2777", "#FCE7F3"),# Pink: Social words / Feelings
    GrammarCategory.TIME_SCHEDULE: ("#7C3AED", "#EDE9FE"),  # Purple: Time / Routines / Sequence
    GrammarCategory.MISC: ("#475569", "#F1F5F9"),           # Slate: Prepositions / Miscellaneous
}

# Curated High-Contrast SVG Icon Definitions for Zero-Latency Offline AAC Boards
SVG_ICONS: Dict[str, str] = {
    "medicine": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><rect x="18" y="8" width="28" height="48" rx="6" fill="#FEE2E2"/><path d="M18 24h28" stroke="#EF4444"/><path d="M32 30v16M24 38h16" stroke="#DC2626" stroke-width="4"/><path d="M26 4h12" stroke="#475569" stroke-width="3"/></svg>',
    "water": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 12l6 40a4 4 0 004 4h12a4 4 0 004-4l6-40H16z" fill="#DBEAFE"/><path d="M18 26c6 2 10-2 14 0s8 2 14 0" stroke="#2563EB" stroke-width="3"/><path d="M32 6v6" stroke="#3B82F6"/></svg>',
    "breakfast": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="34" r="22" fill="#FEF3C7"/><circle cx="32" cy="34" r="14" fill="#FFFFFF" stroke="#F59E0B"/><circle cx="32" cy="34" r="7" fill="#F59E0B"/><path d="M10 14h6v12h-6zM50 14h4v16h-4z" stroke="#64748B"/></svg>',
    "pancakes": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="32" cy="46" rx="22" ry="8" fill="#FDE68A"/><ellipse cx="32" cy="36" rx="20" ry="7" fill="#FCD34D"/><ellipse cx="32" cy="26" rx="18" ry="6" fill="#FBBF24"/><rect x="28" y="16" width="8" height="6" fill="#F59E0B"/></svg>',
    "eggs": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="32" cy="34" rx="20" ry="15" fill="#FFFFFF" stroke="#E2E8F0"/><circle cx="32" cy="34" r="8" fill="#F59E0B"/></svg>',
    "walk": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="36" cy="14" r="6" fill="#22C55E"/><path d="M34 20l-4 16 8 8 6 12M30 36l-8 6-4 10M26 26l8 4 8-4"/></svg>',
    "park": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 48v8M42 48v8" stroke="#78350F" stroke-width="4"/><path d="M22 20c-8 0-12 6-12 12s4 12 12 12 12-6 12-12-4-12-12-12z" fill="#86EFAC"/><path d="M42 16c-8 0-12 6-12 12s4 12 12 12 12-6 12-12-4-12-12-12z" fill="#4ADE80"/><path d="M6 56h52" stroke="#15803D" stroke-width="4"/></svg>',
    "dog": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 30c-4-8-10-8-10 2 0 14 10 20 22 20s22-6 22-20c0-10-6-10-10-2" fill="#FED7AA"/><circle cx="26" cy="32" r="3" fill="#1E293B"/><circle cx="38" cy="32" r="3" fill="#1E293B"/><ellipse cx="32" cy="38" rx="4" ry="3" fill="#1E293B"/><path d="M32 41v3"/></svg>',
    "eat": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 12v18a6 6 0 006 6h2v20h4V36h2a6 6 0 006-6V12" stroke="#16A34A"/><path d="M20 12v12M28 12v12"/><path d="M46 12c-4 0-6 4-6 10v14h4v20h4V12z" fill="#86EFAC" stroke="#16A34A"/></svg>',
    "drink": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 16l6 36a4 4 0 004 4h10a4 4 0 004-4l6-36H18z" fill="#BFDBFE"/><path d="M38 8l6-4M38 8v16" stroke="#2563EB" stroke-width="4"/></svg>',
    "bathroom": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 28h32v12a14 14 0 01-14 14h-4a14 14 0 01-14-14V28z" fill="#E2E8F0"/><path d="M22 14h20v14H22zM28 54v4h8v-4" stroke="#475569"/></svg>',
    "sleep": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><rect x="10" y="32" width="44" height="18" rx="3" fill="#DDD6FE"/><path d="M14 24h12v8H14z" fill="#FFFFFF"/><circle cx="20" cy="28" r="4" fill="#C4B5FD"/><path d="M40 12l8-4-8 8h8M34 18l6-3-6 6h6" stroke="#7C3AED" stroke-width="3"/></svg>',
    "doctor": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="20" r="10" fill="#FEF08A"/><path d="M16 52c0-8.8 7.2-16 16-16s16 7.2 16 16H16z" fill="#BAE6FD"/><path d="M32 40v8M28 44h8" stroke="#DC2626" stroke-width="3.5"/></svg>',
    "happy": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#FBCFE8"/><circle cx="24" cy="28" r="3" fill="#1E293B"/><circle cx="40" cy="28" r="3" fill="#1E293B"/><path d="M22 38c3 6 17 6 20 0" stroke="#DB2777" stroke-width="4"/></svg>',
    "hurt": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#FEE2E2"/><path d="M22 26l6 4M42 26l-6 4M24 42c3-4 13-4 16 0" stroke="#DC2626" stroke-width="4"/><path d="M30 10l-4-4M34 10l4-4" stroke="#DC2626"/></svg>',
    "help": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M32 10v44M10 32h44" stroke="#DC2626" stroke-width="6"/><circle cx="32" cy="32" r="26" stroke="#DC2626" stroke-width="3.5"/></svg>',
    "stop": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="20,8 44,8 56,20 56,44 44,56 20,56 8,44 8,20" fill="#EF4444"/><text x="32" y="38" font-size="14" font-weight="900" text-anchor="middle" fill="#FFFFFF" font-family="sans-serif">STOP</text></svg>',
    "yes": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#DCFCE7"/><path d="M20 32l8 8 16-16" stroke="#16A34A" stroke-width="6"/></svg>',
    "no": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#FEE2E2"/><path d="M20 20l24 24M44 20L20 44" stroke="#DC2626" stroke-width="6"/></svg>',
    "clothes": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12l12 6 12-6 10 12-6 6-4-4v28H20V26l-4 4-6-6 10-12z" fill="#FED7AA"/></svg>',
    "shoes": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 36c4-12 16-16 26-10l12 4c4 2 6 6 6 10v6H12v-10z" fill="#CBD5E1"/><path d="M12 46h44v4H12z" fill="#475569"/></svg>',
    "wash": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="28" cy="28" r="8" fill="#BAE6FD"/><circle cx="40" cy="36" r="6" fill="#BAE6FD"/><circle cx="22" cy="42" r="5" fill="#BAE6FD"/><path d="M16 16c8-6 24-6 32 0" stroke="#0284C7" stroke-width="3"/></svg>',
    "time": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#EDE9FE"/><path d="M32 18v14l10 6" stroke="#7C3AED" stroke-width="4"/></svg>',
    "car": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 36l4-14h28l4 14h6v12H8V36h6z" fill="#BFDBFE"/><circle cx="20" cy="48" r="5" fill="#1E293B"/><circle cx="44" cy="48" r="5" fill="#1E293B"/></svg>',
    "home": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="32,10 8,30 16,30 16,54 48,54 48,30 56,30" fill="#FEF3C7"/><rect x="26" y="34" width="12" height="20" fill="#F59E0B"/></svg>',
    "school": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="32,8 10,22 54,22" fill="#E2E8F0"/><rect x="14" y="22" width="36" height="32" fill="#F8FAFC"/><path d="M32 30v14M26 36h12" stroke="#2563EB" stroke-width="3"/></svg>',
    "music": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 46a6 6 0 11-12 0 6 6 0 0112 0zm32-6a6 6 0 11-12 0 6 6 0 0112 0z" fill="#FBCFE8"/><path d="M22 46V18l32-6v28M22 26l32-6" stroke="#DB2777" stroke-width="4"/></svg>',
    "book": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 16c8-4 18-4 22 2 4-6 14-6 22-2v36c-8-4-18-4-22 2-4-6-14-6-22-2V16z" fill="#FED7AA"/><path d="M32 18v36" stroke="#C2410C" stroke-width="3"/></svg>',
    "play": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#DCFCE7"/><polygon points="26,20 44,32 26,44" fill="#16A34A"/></svg>',
    "listen": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 26a12 12 0 0124 0v16a6 6 0 01-12 0" stroke="#2563EB" stroke-width="4"/><circle cx="20" cy="42" r="5" fill="#93C5FD"/><circle cx="44" cy="42" r="5" fill="#93C5FD"/></svg>',
    "quiet": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="24" r="12" fill="#E2E8F0"/><path d="M32 28v20M24 38h16" stroke="#475569" stroke-width="4"/></svg>',
    "caregiver": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="24" r="8" fill="#FEF08A"/><circle cx="42" cy="18" r="6" fill="#FEF08A"/><path d="M10 52c0-8 6-14 14-14s14 6 14 14H10z" fill="#FDE047"/><path d="M32 52c0-6 4-10 10-10s10 4 10 10H32z" fill="#FACC15"/></svg>',
    "friend": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="22" cy="22" r="7" fill="#FEF08A"/><circle cx="42" cy="22" r="7" fill="#FEF08A"/><path d="M10 52c0-7 5-12 12-12s12 5 12 12H10zm20 0c0-7 5-12 12-12s12 5 12 12H30z" fill="#FDE047"/></svg>',
    "bus": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="14" width="40" height="34" rx="4" fill="#FDE047"/><rect x="16" y="20" width="32" height="12" fill="#BAE6FD"/><circle cx="20" cy="48" r="4" fill="#1E293B"/><circle cx="44" cy="48" r="4" fill="#1E293B"/></svg>',
    "teeth": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 16c-6 0-10 8-8 20s4 18 10 18 6-10 10-10 4 10 10 10 8-6 10-18-2-20-8-20-8 4-12 4-8-4-12-4z" fill="#FFFFFF" stroke="#64748B"/><path d="M12 14l40 36" stroke="#0284C7" stroke-width="3"/></svg>',
    "snack": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="34" r="18" fill="#FED7AA"/><circle cx="26" cy="28" r="2.5" fill="#7C2D12"/><circle cx="38" cy="30" r="2.5" fill="#7C2D12"/><circle cx="30" cy="40" r="2.5" fill="#7C2D12"/><circle cx="40" cy="40" r="2" fill="#7C2D12"/></svg>',
    "apple": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M32 20c-6-6-16-4-18 6-2 14 8 26 18 26s20-12 18-26c-2-10-12-12-18-6z" fill="#F87171"/><path d="M32 20c0-6 4-10 8-10" stroke="#15803D" stroke-width="3"/></svg>',
    "juice": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><rect x="18" y="20" width="28" height="34" rx="3" fill="#FDBA74"/><polygon points="18,20 26,10 38,10 46,20" fill="#FB923C"/><path d="M32 6l10-4" stroke="#EA580C" stroke-width="3.5"/></svg>',
    "milk": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 14h20v6H22z" fill="#E2E8F0"/><path d="M20 20l-4 6v28a2 2 0 002 2h28a2 2 0 002-2V26l-4-6H20z" fill="#F8FAFC"/><text x="32" y="42" font-size="10" font-weight="bold" text-anchor="middle" fill="#0284C7">MILK</text></svg>',
    "lunch": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="22" width="40" height="28" rx="4" fill="#FED7AA"/><path d="M12 28h40M26 14h12v8H26z" stroke="#C2410C"/></svg>',
    "tired": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#F3E8FF"/><path d="M22 28h8M34 28h8M28 40a4 4 0 108 0 4 4 0 00-8 0" stroke="#7C3AED" stroke-width="3.5"/><path d="M46 14l6-3-6 6h6" stroke="#9333EA"/></svg>',
    "calm": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#E0F2FE"/><path d="M22 28c2-2 6-2 8 0M34 28c2-2 6-2 8 0M26 38c3 2 9 2 12 0" stroke="#0284C7" stroke-width="3.5"/></svg>',
    "now": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#EDE9FE"/><path d="M32 20v24M24 36l8 8 8-8" stroke="#7C3AED" stroke-width="4"/></svg>',
    "later": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#EDE9FE"/><path d="M20 32h24M36 24l8 8-8 8" stroke="#7C3AED" stroke-width="4"/></svg>',
    "all_done": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#DCFCE7"/><path d="M18 34l8 8 20-20" stroke="#16A34A" stroke-width="5"/><path d="M12 50h40" stroke="#16A34A" stroke-width="4"/></svg>',
    "more": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="24" fill="#FCE7F3"/><path d="M32 18v28M18 32h28" stroke="#DB2777" stroke-width="5"/></svg>',
    "toilet": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 28h28v12a14 14 0 01-14 14h0a14 14 0 01-14-14V28z" fill="#E2E8F0"/><path d="M22 14h20v14H22z" stroke="#475569"/></svg>',
}

# ARASAAC Canonical Catalog Mappings (Open-license AAC Pictograms)
# Arasaac IDs can also be resolved dynamically from ARASAAC API
ARASAAC_CATALOG: Dict[str, Dict] = {
    "medicine": {"arasaac_id": 2439, "category": GrammarCategory.NOUN, "tags": ["pills", "pill", "medication", "tablet", "syrup", "capsule"]},
    "water": {"arasaac_id": 2459, "category": GrammarCategory.NOUN, "tags": ["drink", "glass", "beverage", "hydration"]},
    "breakfast": {"arasaac_id": 2351, "category": GrammarCategory.NOUN, "tags": ["morning", "food", "meal", "eat"]},
    "pancakes": {"arasaac_id": 34185, "category": GrammarCategory.NOUN, "tags": ["food", "breakfast", "hotcakes", "syrup"]},
    "eggs": {"arasaac_id": 2364, "category": GrammarCategory.NOUN, "tags": ["egg", "scrambled", "omelette", "breakfast"]},
    "walk": {"arasaac_id": 2552, "category": GrammarCategory.VERB, "tags": ["walking", "step", "stroll", "go"]},
    "park": {"arasaac_id": 2865, "category": GrammarCategory.NOUN, "tags": ["outside", "garden", "playground", "nature"]},
    "dog": {"arasaac_id": 2465, "category": GrammarCategory.NOUN, "tags": ["dogs", "puppy", "pet", "animal"]},
    "eat": {"arasaac_id": 2363, "category": GrammarCategory.VERB, "tags": ["eating", "food", "meal", "dine", "snack"]},
    "drink": {"arasaac_id": 2358, "category": GrammarCategory.VERB, "tags": ["drinking", "sip", "gulp", "thirst"]},
    "bathroom": {"arasaac_id": 2404, "category": GrammarCategory.NOUN, "tags": ["toilet", "potty", "washroom", "restroom", "pee", "poop"]},
    "toilet": {"arasaac_id": 2404, "category": GrammarCategory.NOUN, "tags": ["bathroom", "potty", "restroom"]},
    "sleep": {"arasaac_id": 2529, "category": GrammarCategory.VERB, "tags": ["nap", "bed", "rest", "night", "sleeping"]},
    "doctor": {"arasaac_id": 2399, "category": GrammarCategory.PEOPLE, "tags": ["physician", "clinic", "hospital", "pediatrician"]},
    "happy": {"arasaac_id": 2434, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["glad", "smile", "joy", "good", "great"]},
    "hurt": {"arasaac_id": 2442, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["pain", "ouch", "injury", "sick", "wound"]},
    "help": {"arasaac_id": 2435, "category": GrammarCategory.VERB, "tags": ["assist", "aid", "support", "emergency"]},
    "stop": {"arasaac_id": 2534, "category": GrammarCategory.VERB, "tags": ["halt", "no", "end", "pause", "wait"]},
    "yes": {"arasaac_id": 2568, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["ok", "agree", "correct", "sure", "yep"]},
    "no": {"arasaac_id": 2469, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["not", "dont", "never", "refuse"]},
    "clothes": {"arasaac_id": 2415, "category": GrammarCategory.NOUN, "tags": ["shirt", "pants", "dress", "get dressed", "clothing"]},
    "shoes": {"arasaac_id": 2525, "category": GrammarCategory.NOUN, "tags": ["sneakers", "boots", "footwear"]},
    "wash": {"arasaac_id": 2555, "category": GrammarCategory.VERB, "tags": ["hands", "clean", "soap", "sink", "washing"]},
    "time": {"arasaac_id": 2542, "category": GrammarCategory.TIME_SCHEDULE, "tags": ["clock", "schedule", "hour", "minute"]},
    "car": {"arasaac_id": 2408, "category": GrammarCategory.NOUN, "tags": ["drive", "ride", "auto", "vehicle"]},
    "home": {"arasaac_id": 2436, "category": GrammarCategory.NOUN, "tags": ["house", "room", "stay"]},
    "school": {"arasaac_id": 2521, "category": GrammarCategory.NOUN, "tags": ["class", "study", "teacher", "learning"]},
    "music": {"arasaac_id": 2467, "category": GrammarCategory.NOUN, "tags": ["song", "listen", "dance", "audio"]},
    "book": {"arasaac_id": 2403, "category": GrammarCategory.NOUN, "tags": ["read", "story", "reading"]},
    "play": {"arasaac_id": 2496, "category": GrammarCategory.VERB, "tags": ["game", "toy", "fun", "playing"]},
    "listen": {"arasaac_id": 2454, "category": GrammarCategory.VERB, "tags": ["hear", "sound", "music"]},
    "quiet": {"arasaac_id": 2506, "category": GrammarCategory.ADJECTIVE, "tags": ["shh", "calm", "silence", "soft"]},
    "caregiver": {"arasaac_id": 2410, "category": GrammarCategory.PEOPLE, "tags": ["mom", "dad", "parent", "helper", "nurse", "aide"]},
    "friend": {"arasaac_id": 2430, "category": GrammarCategory.PEOPLE, "tags": ["buddy", "peer", "playmate"]},
    "bus": {"arasaac_id": 2406, "category": GrammarCategory.NOUN, "tags": ["transit", "schoolbus", "ride"]},
    "teeth": {"arasaac_id": 2540, "category": GrammarCategory.NOUN, "tags": ["brush teeth", "toothbrush", "mouth", "dental"]},
    "snack": {"arasaac_id": 2530, "category": GrammarCategory.NOUN, "tags": ["cookie", "treat", "crackers", "bites"]},
    "apple": {"arasaac_id": 2335, "category": GrammarCategory.NOUN, "tags": ["fruit", "healthy", "snack"]},
    "juice": {"arasaac_id": 2447, "category": GrammarCategory.NOUN, "tags": ["orange juice", "apple juice", "drink"]},
    "milk": {"arasaac_id": 2463, "category": GrammarCategory.NOUN, "tags": ["dairy", "drink", "cup"]},
    "lunch": {"arasaac_id": 2458, "category": GrammarCategory.NOUN, "tags": ["afternoon meal", "food", "sandwich"]},
    "tired": {"arasaac_id": 2543, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["sleepy", "exhausted", "rest"]},
    "calm": {"arasaac_id": 2407, "category": GrammarCategory.ADJECTIVE, "tags": ["peaceful", "relax", "breathe", "gentle"]},
    "now": {"arasaac_id": 2470, "category": GrammarCategory.TIME_SCHEDULE, "tags": ["immediate", "first", "current"]},
    "later": {"arasaac_id": 2451, "category": GrammarCategory.TIME_SCHEDULE, "tags": ["then", "after", "next"]},
    "all_done": {"arasaac_id": 2426, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["finished", "complete", "done", "stop"]},
    "more": {"arasaac_id": 2466, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["again", "extra", "add"]},
}


def normalize_term(term: str) -> str:
    """Normalize input term for fuzzy matching."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s_]", "", term.lower().strip())
    return cleaned.replace(" ", "_")


class SymbolResolver:
    """
    Resolves simplified AAC concepts to high-contrast picture symbols,
    ARASAAC identifiers, or graceful text-card fallbacks.
    """

    def __init__(self):
        self.catalog = ARASAAC_CATALOG
        self.svg_icons = SVG_ICONS
        self.palette = FITZGERALD_PALETTE

    def resolve_concept(
        self,
        concept: str,
        category_hint: Optional[str] = None,
        preferred_symbol_id: Optional[str] = None
    ) -> SymbolCard:
        """
        Resolves a single concept into a complete SymbolCard.
        Applies recipient preference override if supplied.
        """
        norm_concept = normalize_term(concept)

        # 1. Direct match in local catalog
        if norm_concept in self.catalog:
            item = self.catalog[norm_concept]
            category = item["category"]
            color_code, bg_color = self.palette[category]
            arasaac_id = item.get("arasaac_id")
            svg_icon = self.svg_icons.get(norm_concept)
            
            # ARASAAC Open-CDN image URL
            image_url = f"https://static.arasaac.org/pictograms/{arasaac_id}/{arasaac_id}_500.png" if arasaac_id else None

            return SymbolCard(
                id=f"sym_{norm_concept}",
                word=concept.upper(),
                category=category,
                color_code=color_code,
                bg_color=bg_color,
                image_url=image_url,
                svg_icon=svg_icon,
                arasaac_id=arasaac_id,
                source=SymbolSource.CURATED_AAC if svg_icon else SymbolSource.ARASAAC,
                confidence=1.0,
                is_fallback=False,
                pronunciation_hint=concept.title()
            )

        # 2. Tag / Synonym Match
        for key, item in self.catalog.items():
            if norm_concept in item.get("tags", []) or any(norm_concept in tag for tag in item.get("tags", [])):
                category = item["category"]
                color_code, bg_color = self.palette[category]
                arasaac_id = item.get("arasaac_id")
                svg_icon = self.svg_icons.get(key)
                image_url = f"https://static.arasaac.org/pictograms/{arasaac_id}/{arasaac_id}_500.png" if arasaac_id else None

                return SymbolCard(
                    id=f"sym_{key}",
                    word=concept.upper(),
                    category=category,
                    color_code=color_code,
                    bg_color=bg_color,
                    image_url=image_url,
                    svg_icon=svg_icon,
                    arasaac_id=arasaac_id,
                    source=SymbolSource.CURATED_AAC if svg_icon else SymbolSource.ARASAAC,
                    confidence=0.9,
                    is_fallback=False,
                    pronunciation_hint=concept.title(),
                    subtext=f"Mapped to: {key.title()}"
                )

        # 3. Category classification & Fallback Card
        category = self._infer_category(concept, category_hint)
        color_code, bg_color = self.palette[category]
        
        # Check if we have an SVG icon under sanitized name
        svg_icon = self.svg_icons.get(norm_concept)

        return SymbolCard(
            id=f"card_{norm_concept}",
            word=concept.upper(),
            category=category,
            color_code=color_code,
            bg_color=bg_color,
            image_url=None,
            svg_icon=svg_icon,
            arasaac_id=None,
            source=SymbolSource.TEXT_FALLBACK if not svg_icon else SymbolSource.CURATED_AAC,
            confidence=0.75 if svg_icon else 0.5,
            is_fallback=(svg_icon is None),
            pronunciation_hint=concept.title(),
            subtext="Text Card" if not svg_icon else None
        )

    def _infer_category(self, concept: str, category_hint: Optional[str]) -> GrammarCategory:
        """Infer grammatical category for Fitzgerald Key color coding."""
        if category_hint:
            try:
                return GrammarCategory(category_hint.lower())
            except ValueError:
                pass

        lower = concept.lower()
        if lower in ["i", "you", "we", "he", "she", "mom", "dad", "doctor", "nurse", "friend", "teacher", "me"]:
            return GrammarCategory.PEOPLE
        if lower in ["eat", "drink", "walk", "go", "stop", "help", "take", "sleep", "wash", "play", "see", "want", "like"]:
            return GrammarCategory.VERB
        if lower in ["happy", "sad", "hurt", "tired", "good", "bad", "calm", "please", "thanks", "yes", "no", "more"]:
            return GrammarCategory.SOCIAL_FEELINGS
        if lower in ["now", "later", "morning", "afternoon", "night", "today", "tomorrow", "first", "then"]:
            return GrammarCategory.TIME_SCHEDULE
        if lower in ["big", "small", "hot", "cold", "fast", "slow", "red", "blue"]:
            return GrammarCategory.ADJECTIVE
        return GrammarCategory.NOUN

    def search_symbols(self, query: str, limit: int = 10) -> List[Dict]:
        """Search available symbols by keyword."""
        q = normalize_term(query)
        results = []
        for key, item in self.catalog.items():
            if q in key or any(q in tag for tag in item.get("tags", [])):
                results.append({
                    "id": key,
                    "word": key.title(),
                    "category": item["category"].value,
                    "arasaac_id": item.get("arasaac_id"),
                    "has_svg": key in self.svg_icons
                })
                if len(results) >= limit:
                    break
        return results


# Singleton instance
symbol_resolver = SymbolResolver()
