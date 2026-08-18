"""
AAC Symbol Library and Resolver.
Provides open-license AAC pictograms (ARASAAC and premium high-contrast vector illustrations)
with Fitzgerald Key color coding and graceful text-card fallback.
"""

import re
from typing import Dict, List, Optional, Tuple
from communicare.models import GrammarCategory, SymbolCard, SymbolSource

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

# Premium, Friendly, High-Contrast Vector AAC Pictograms
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

    "eat": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 16V36C20 42 26 46 30 46V68" stroke="#10B981" stroke-width="4" stroke-linecap="round"/>
      <path d="M25 16V32M15 16V32" stroke="#10B981" stroke-width="3" stroke-linecap="round"/>
      <path d="M56 16C50 16 46 22 46 32C46 42 50 46 54 46V68" stroke="#10B981" stroke-width="4" stroke-linecap="round"/>
      <circle cx="40" cy="50" r="16" fill="#D1FAE5" opacity="0.6"/>
    </svg>''',

    "drink": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="26" y="24" width="28" height="42" rx="4" fill="#DBEAFE" stroke="#2563EB" stroke-width="3.5"/>
      <path d="M26 38H54" stroke="#3B82F6" stroke-width="2.5"/>
      <path d="M48 10L56 18M48 10V24" stroke="#EA580C" stroke-width="4" stroke-linecap="round"/>
    </svg>''',

    "bathroom": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="26" y="16" width="28" height="20" rx="3" fill="#E2E8F0" stroke="#475569" stroke-width="3"/>
      <path d="M20 36H60C60 52 50 64 40 64C30 64 20 52 20 36Z" fill="#F8FAFC" stroke="#475569" stroke-width="3.5"/>
      <rect x="34" y="64" width="12" height="6" fill="#64748B"/>
    </svg>''',

    "toilet": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="26" y="16" width="28" height="20" rx="3" fill="#E2E8F0" stroke="#475569" stroke-width="3"/>
      <path d="M20 36H60C60 52 50 64 40 64C30 64 20 52 20 36Z" fill="#F8FAFC" stroke="#475569" stroke-width="3.5"/>
      <rect x="34" y="64" width="12" height="6" fill="#64748B"/>
    </svg>''',

    "sleep": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="14" y="42" width="52" height="22" rx="4" fill="#EDE9FE" stroke="#7C3AED" stroke-width="3.5"/>
      <rect x="18" y="32" width="16" height="12" rx="3" fill="#FFFFFF" stroke="#A78BFA" stroke-width="2.5"/>
      <circle cx="26" cy="38" r="4" fill="#C4B5FD"/>
      <path d="M48 18L58 14L48 24H58" stroke="#8B5CF6" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M40 26L48 23L40 31H48" stroke="#A78BFA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
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

    "help": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#FEF2F2" stroke="#EF4444" stroke-width="4"/>
      <rect x="35" y="20" width="10" height="40" rx="2" fill="#DC2626"/>
      <rect x="20" y="35" width="40" height="10" rx="2" fill="#DC2626"/>
    </svg>''',

    "stop": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polygon points="26,10 54,10 68,24 68,56 54,70 26,70 12,56 12,24" fill="#EF4444" stroke="#B91C1C" stroke-width="3"/>
      <text x="40" y="47" font-size="16" font-weight="900" text-anchor="middle" fill="#FFFFFF" font-family="system-ui, sans-serif" letter-spacing="1">STOP</text>
    </svg>''',

    "yes": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#DCFCE7" stroke="#16A34A" stroke-width="3.5"/>
      <path d="M26 40L36 50L54 28" stroke="#15803D" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>''',

    "no": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#FEE2E2" stroke="#DC2626" stroke-width="3.5"/>
      <path d="M26 26L54 54M54 26L26 54" stroke="#B91C1C" stroke-width="6" stroke-linecap="round"/>
    </svg>''',

    "clothes": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M26 18L40 24L54 18L66 32L58 40L54 36V66H26V36L22 40L14 32L26 18Z" fill="#FED7AA" stroke="#EA580C" stroke-width="3.5" stroke-linejoin="round"/>
      <circle cx="40" cy="38" r="2.5" fill="#9A3412"/>
      <circle cx="40" cy="48" r="2.5" fill="#9A3412"/>
    </svg>''',

    "shoes": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 46C20 30 36 26 50 32L64 36C68 38 70 42 70 48V56H16V46Z" fill="#E2E8F0" stroke="#475569" stroke-width="3.5" stroke-linejoin="round"/>
      <rect x="16" y="56" width="54" height="6" rx="2" fill="#334155"/>
      <path d="M36 34L42 46M44 36L50 46" stroke="#0284C7" stroke-width="2.5" stroke-linecap="round"/>
    </svg>''',

    "wash": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="32" cy="36" r="10" fill="#BAE6FD" stroke="#0284C7" stroke-width="2.5"/>
      <circle cx="48" cy="44" r="8" fill="#BAE6FD" stroke="#0284C7" stroke-width="2.5"/>
      <circle cx="28" cy="52" r="6" fill="#BAE6FD" stroke="#0284C7" stroke-width="2"/>
      <path d="M22 22C32 14 50 14 60 22" stroke="#0369A1" stroke-width="4" stroke-linecap="round"/>
    </svg>''',

    "time": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#F5F3FF" stroke="#7C3AED" stroke-width="3.5"/>
      <path d="M40 22V40L52 46" stroke="#6D28D9" stroke-width="4.5" stroke-linecap="round"/>
      <circle cx="40" cy="40" r="3" fill="#5B21B6"/>
    </svg>''',

    "school": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polygon points="40,12 14,28 66,28" fill="#FEE2E2" stroke="#DC2626" stroke-width="3"/>
      <rect x="18" y="28" width="44" height="38" fill="#F8FAFC" stroke="#475569" stroke-width="3"/>
      <rect x="34" y="46" width="12" height="20" fill="#D97706"/>
      <circle cx="40" cy="22" r="4" fill="#FBBF24"/>
    </svg>''',

    "bus": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="14" y="18" width="52" height="42" rx="6" fill="#FDE047" stroke="#CA8A04" stroke-width="3.5"/>
      <rect x="20" y="26" width="40" height="14" rx="2" fill="#E0F2FE" stroke="#0284C7" stroke-width="2"/>
      <circle cx="26" cy="60" r="6" fill="#1E293B" stroke="#0F172A" stroke-width="2"/>
      <circle cx="54" cy="60" r="6" fill="#1E293B" stroke="#0F172A" stroke-width="2"/>
    </svg>''',

    "teeth": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M26 22C20 22 14 30 16 46C18 58 24 64 30 64C36 64 36 50 40 50C44 50 44 64 50 64C56 64 62 58 64 46C66 30 60 22 54 22C46 22 44 28 40 28C36 28 34 22 26 22Z" fill="#FFFFFF" stroke="#64748B" stroke-width="3.5"/>
      <path d="M16 20L64 60" stroke="#0284C7" stroke-width="4" stroke-linecap="round"/>
    </svg>''',

    "apple": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M40 26C32 18 18 20 18 36C18 54 32 66 40 66C48 66 62 54 62 36C62 20 48 18 40 26Z" fill="#EF4444" stroke="#B91C1C" stroke-width="3.5"/>
      <path d="M40 26C40 16 46 14 50 12" stroke="#15803D" stroke-width="3.5" stroke-linecap="round"/>
      <circle cx="48" cy="34" r="3" fill="#FCA5A5"/>
    </svg>''',

    "juice": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="24" y="24" width="32" height="44" rx="4" fill="#FED7AA" stroke="#EA580C" stroke-width="3.5"/>
      <polygon points="24,24 34,14 46,14 56,24" fill="#FB923C" stroke="#EA580C" stroke-width="2.5"/>
      <path d="M40 8L50 4" stroke="#C2410C" stroke-width="3.5" stroke-linecap="round"/>
      <circle cx="40" cy="46" r="6" fill="#F97316"/>
    </svg>''',

    "book": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 22C24 16 36 16 40 22C44 16 56 16 66 22V64C56 58 44 58 40 64C36 58 24 58 14 64V22Z" fill="#FED7AA" stroke="#EA580C" stroke-width="3.5" stroke-linejoin="round"/>
      <path d="M40 24V64" stroke="#9A3412" stroke-width="3.5"/>
    </svg>''',

    "quiet": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="32" r="16" fill="#E0F2FE" stroke="#0284C7" stroke-width="3"/>
      <path d="M40 38V64M30 52H50" stroke="#0369A1" stroke-width="5" stroke-linecap="round"/>
    </svg>''',

    "music": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="56" r="8" fill="#FBCFE8" stroke="#DB2777" stroke-width="3"/>
      <circle cx="56" cy="48" r="8" fill="#FBCFE8" stroke="#DB2777" stroke-width="3"/>
      <path d="M36 56V24L64 16V48" stroke="#BE185D" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M36 34L64 26" stroke="#BE185D" stroke-width="4.5"/>
    </svg>''',

    "snack": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="42" r="22" fill="#FED7AA" stroke="#EA580C" stroke-width="3.5"/>
      <circle cx="32" cy="36" r="3.5" fill="#7C2D12"/>
      <circle cx="48" cy="38" r="3.5" fill="#7C2D12"/>
      <circle cx="38" cy="50" r="3.5" fill="#7C2D12"/>
      <circle cx="48" cy="50" r="2.5" fill="#7C2D12"/>
    </svg>''',
    
    "tired": '''<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="40" cy="40" r="30" fill="#F5F3FF" stroke="#7C3AED" stroke-width="3.5"/>
      <path d="M26 34H36M44 34H54" stroke="#6D28D9" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M34 50C36 54 44 54 46 50" stroke="#7C3AED" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M56 18L64 14L56 22H64" stroke="#8B5CF6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>'''
}

# ARASAAC Canonical Catalog
ARASAAC_CATALOG: Dict[str, Dict] = {
    "medicine": {"arasaac_id": 2439, "category": GrammarCategory.NOUN, "tags": ["pills", "pill", "medication", "tablet", "syrup", "capsule"]},
    "water": {"arasaac_id": 2459, "category": GrammarCategory.NOUN, "tags": ["drink", "glass", "beverage", "hydration"]},
    "breakfast": {"arasaac_id": 2351, "category": GrammarCategory.NOUN, "tags": ["morning", "food", "meal", "eat"]},
    "pancakes": {"arasaac_id": 34185, "category": GrammarCategory.NOUN, "tags": ["food", "breakfast", "hotcakes", "syrup"]},
    "eggs": {"arasaac_id": 2364, "category": GrammarCategory.NOUN, "tags": ["egg", "scrambled", "omelette", "breakfast"]},
    "walk": {"arasaac_id": 2552, "category": GrammarCategory.VERB, "tags": ["walking", "step", "stroll", "go"]},
    "park": {"arasaac_id": 2865, "category": GrammarCategory.NOUN, "tags": ["outside", "garden", "playground", "nature"]},
    "dog": {"arasaac_id": 2465, "category": GrammarCategory.NOUN, "tags": ["dogs", "puppy", "pet", "animal"]},
    "morning": {"arasaac_id": 2470, "category": GrammarCategory.TIME_SCHEDULE, "tags": ["am", "sunrise", "early", "routine"]},
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
    "school": {"arasaac_id": 2521, "category": GrammarCategory.NOUN, "tags": ["class", "study", "teacher", "learning"]},
    "bus": {"arasaac_id": 2406, "category": GrammarCategory.NOUN, "tags": ["transit", "schoolbus", "ride"]},
    "teeth": {"arasaac_id": 2540, "category": GrammarCategory.NOUN, "tags": ["brush teeth", "toothbrush", "mouth", "dental"]},
    "apple": {"arasaac_id": 2335, "category": GrammarCategory.NOUN, "tags": ["fruit", "healthy", "snack"]},
    "juice": {"arasaac_id": 2447, "category": GrammarCategory.NOUN, "tags": ["orange juice", "apple juice", "drink"]},
    "book": {"arasaac_id": 2403, "category": GrammarCategory.NOUN, "tags": ["read", "story", "reading"]},
    "quiet": {"arasaac_id": 2506, "category": GrammarCategory.ADJECTIVE, "tags": ["shh", "calm", "silence", "soft"]},
    "music": {"arasaac_id": 2467, "category": GrammarCategory.NOUN, "tags": ["song", "listen", "dance", "audio"]},
    "snack": {"arasaac_id": 2530, "category": GrammarCategory.NOUN, "tags": ["cookie", "treat", "crackers", "bites"]},
    "tired": {"arasaac_id": 2543, "category": GrammarCategory.SOCIAL_FEELINGS, "tags": ["sleepy", "exhausted", "rest"]}
}


def normalize_term(term: str) -> str:
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
        norm_concept = normalize_term(concept)

        # 1. Direct match in local catalog
        if norm_concept in self.catalog:
            item = self.catalog[norm_concept]
            category = item["category"]
            color_code, bg_color, _ = self.palette[category]
            arasaac_id = item.get("arasaac_id")
            svg_icon = self.svg_icons.get(norm_concept)
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
                color_code, bg_color, _ = self.palette[category]
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
        color_code, bg_color, _ = self.palette[category]
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


symbol_resolver = SymbolResolver()
