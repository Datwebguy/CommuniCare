# CommuniCare | Autonomous AAC Picture Symbol Board Platform
## Comprehensive Technical Architecture, Implementation Report, and Strategic Analysis

---

### Executive Summary

**CommuniCare** is an autonomous clinical assistive intelligence platform that converts natural language caregiver messages, routine instructions, and therapy notes into plain language sentences and high contrast AAC (Augmentative and Alternative Communication) picture symbol boards for nonverbal individuals.

Traditional AAC board creation requires Speech Language Pathologists (SLPs) and caregivers to manually search symbol catalogs, resize tiles, format color coding, and print or configure communication sheets. This manual chore takes 15 to 30 minutes per daily routine. CommuniCare executes this end to end workflow in under one second, personalizing vocabulary and symbols based on individual recipient history.

---

### Core Architecture and Autonomous 5 Step Pipeline

The platform operates on a pipeline architecture:

```
[ Natural Caregiver Message ] 
             ↓
[ Step 1: Memory and Profile Lookup (Firestore) ]
             ↓
[ Step 2: Language Simplification and Concept Extraction (Gemini 2.5 Flash) ]
             ↓
[ Step 3: Symbol Resolution and Disambiguation (Live ARASAAC API and Curated Vectors) ]
             ↓
[ Step 4: High Contrast Board Assembly (Fitzgerald Key Clinical Standard) ]
             ↓
[ Step 5: State Persistence and Multi Turn Learning (Firestore) ]
             ↓
[ Dynamic AAC Board Output (Web Speech Audio TTS, Print Sheet, Presentation Mode) ]
```

#### Step 1: Profile and Memory Lookup
* **Service**: `communicare/services/firestore_service.py`
* **Function**: Retrieves the care recipient individualized cognitive profile, age group (*Child / Teen / Adult*), vocabulary ceiling (*Basic 4 cards / Intermediate 6 cards / Advanced 8 to 10 cards*), reinforced vocabulary history, and custom symbol overrides.
* **Multi Tenant Isolation**: Every profile is scoped to the authenticated caregiver workspace (`caregivers/{caregiver_id}/recipients/{recipient_id}`), preventing cross user data leakage.

#### Step 2: Language Simplification and Reasoning
* **Service**: `communicare/services/gemini_service.py`
* **Model**: Google Gemini 2.5 Flash (with resilient rule based NLP fallback for offline and local testing).
* **Function**: Ingests unstructured caregiver speech, extracts core conversational intent, strips grammatical filler, and outputs structured JSON containing essential communication concepts mapped to parts of speech.

#### Step 3: Dynamic Symbol Resolution and Disambiguation
* **Service**: `communicare/services/symbol_library.py`
* **Data Sources**:
  1. **Live Open ARASAAC REST API**: Direct querying of the global ARASAAC pictogram catalog (`https://api.arasaac.org/api/pictograms/en/search/{term}`) with in memory caching, supporting tens of thousands of English words dynamically.
  2. **Curated High Contrast Vector SVGs**: Handcrafted vector illustrations for high frequency daily needs (*Medicine, Water, Pancakes, Walk, Park, Doctor, Happy, Sleep, etc.*).
  3. **Graceful Text Fallbacks**: Accessible typographic cards for specialized or uncatalogued medical terms, ensuring zero pipeline crashes.

#### Step 4: Board Assembly and Fitzgerald Key Syntax
* **Standard**: Clinical Fitzgerald Key color coding convention used by Speech Language Pathologists:
  * **Yellow**: People and Pronouns (`#EAB308` border, `#FEFCE8` soft bg)
  * **Green**: Verbs and Actions (`#10B981` border, `#ECFDF5` soft bg)
  * **Orange**: Nouns, Objects, and Foods (`#F97316` border, `#FFF7ED` soft bg)
  * **Blue**: Adjectives and Descriptors (`#3B82F6` border, `#EFF6FF` soft bg)
  * **Pink**: Feelings and Social Words (`#EC4899` border, `#FDF2F8` soft bg)
  * **Purple**: Time, Schedule, and Routine Sequence (`#8B5CF6` border, `#F5F3FF` soft bg)
* **Layout**: Balanced 3×2 grid canvas engineered for physical printouts and touch tablets.

#### Step 5: Memory Persistence and Adaptive Learning
* **Function**: Automatically updates vocabulary encounter frequencies in Firestore.
* **Feedback Loop**: Caregiver one click *"Worked Well"* button reinforces successful communication tokens, prioritizing familiar symbols in subsequent sessions.

---

### Voice and Speech Customization Engine

Located in `communicare/static/app.js` with audio settings modal:
1. **Voice Personas and Tones**:
   * 🧒 **Child Friendly**: High pitch (`1.40x`), warm tone, friendly articulation.
   * 👩 **Female Adult**: Natural pitch (`1.05x`), gentle conversational tone.
   * 👨 **Male Adult**: Grounded pitch (`0.85x`), clear steady tone.
   * 🌿 **Gentle and Calm**: Slower rate (`0.72x`), soft tone for sensory sensitivities.
   * ✨ **Expressive**: Dynamic pitch (`1.25x`), lively articulation.
   * ⚙️ **Custom System Voice**: Direct dropdown of all local browser and operating system voices (`speechSynthesis.getVoices()`).
2. **Pitch and Speed Sliders**: Live adjustable sliders with real time numeric labels.
3. **Promise Based Speech Sequencer**: Uses `utterance.onend` listeners to reliably vocalize 100% of cards in sequence without clipping or dropping words.
4. **Visual Speech Focus**: Active card glows with a Midnight Wine outline (`.card-speaking`) during vocalization.

---

### Design System and Color Architecture

Built according to the **Superhuman Golden Hour Editorial Canvas** design specification:

| Token Name | Hex Value | Role in CommuniCare |
|---|---|---|
| **Warm Parchment** | `#f2f0eb` | Primary page canvas and soft card backgrounds |
| **Midnight Wine** | `#421d24` | Primary action buttons, brand icon, footer, and active speaking rings |
| **Royal Violet** | `#714cb6` | Section badges, secondary links, and emphasis tags |
| **Lilac Mist** | `#d4c7ff` | Scenario chips, intent badges, and secondary button fills |
| **Deep Lagoon** | `#0c4243` | Full bleed dark architectural feature band on landing page |
| **Soft Mist** | `#e3e3e2` | Hairline borders, dividers, and card outlines |
| **Ink Charcoal** | `#292827` | High contrast primary headings and body copy |
| **Stone Gray** | `#666666` | Secondary helper descriptions and metadata labels |
| **Paper White** | `#ffffff` | Elevated studio cards, board canvas, and modals |

---

### Project File Structure

```
CommuniCare/
├── Dockerfile                         # Production Cloud Run container config
├── cloudbuild.yaml                    # Google Cloud Build deployment pipeline
├── requirements.txt                   # Python dependencies (FastAPI, Google GenAI, Uvicorn, Requests)
├── PROJECT_OVERVIEW_AND_ANALYSIS.md   # Complete project documentation and strategic roadmap
├── data/
│   ├── recipient_profiles.json        # Persistent local JSON fallback store
│   └── presets.json                   # Dynamic care routine presets
├── communicare/
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # FastAPI application entrypoint and routing
│   ├── api.py                         # REST API endpoints (Boards, Recipients, Presets, Feedback, Health)
│   ├── models.py                      # Pydantic data schemas and Fitzgerald Key enums
│   ├── agent/
│   │   └── pipeline.py                # 5 step autonomous orchestrator
│   ├── services/
│   │   ├── gemini_service.py          # Gemini 2.5 Flash structured reasoning service
│   │   ├── firestore_service.py       # Multi tenant Firestore and local JSON state engine
│   │   └── symbol_library.py          # Live ARASAAC REST API resolver and vector SVG catalog
│   └── static/
│       ├── landing.html               # Superhuman editorial landing page
│       ├── landing.css                # Dedicated landing page stylesheet
│       ├── landing.js                 # Landing page tab switcher and live preview sandbox
│       ├── index.html                 # Interactive Caregiver Studio and AAC Board Generator
│       ├── style.css                  # Studio stylesheet matching the editorial palette
│       ├── app.js                     # Full frontend state controller and Web Speech engine
│       └── images/
│           ├── hero_editorial.jpg     # Warm golden hour hero background
│           └── dark_feature_art.jpg   # Deep Lagoon feature background
└── tests/
    ├── test_agent_pipeline.py         # End to end pipeline and multi turn adaptation tests
    ├── test_api.py                    # REST API status, headers, and validation tests
    ├── test_firestore_memory.py       # CRUD and multi tenant memory tests
    └── test_symbol_resolver.py        # ARASAAC matching, vector SVG, and fallback tests
```

---

### API Specification and Endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/generate-board` | Ingests caregiver message and generates full AAC response |
| `GET` | `/api/recipients` | Lists recipient profiles scoped to requesting caregiver |
| `GET` | `/api/recipients/{id}` | Retrieves specific recipient profile and vocabulary history |
| `POST` | `/api/recipients` | Creates or updates a recipient profile in Firestore |
| `DELETE` | `/api/recipients/{id}` | Deletes a recipient profile safely |
| `POST` | `/api/feedback` | Records card feedback and reinforces vocabulary |
| `GET` | `/api/presets` | Retrieves dynamic care routine presets |
| `POST` | `/api/presets` | Creates a new care routine preset |
| `GET` | `/api/symbols/search` | Dynamic search across ARASAAC and vector icons |
| `GET` | `/api/health` | System health check and status diagnostics |
| `GET` | `/` or `/landing` | Serves Superhuman editorial landing page |
| `GET` | `/app` | Serves interactive Caregiver AAC Studio |

---

### Verification and Test Results

All **19 automated unit and integration tests** pass consistently:
* `tests/test_agent_pipeline.py`: PASSED (Morning routine generation, multi turn adaptation)
* `tests/test_api.py`: PASSED (Healthcheck, generate board, empty validation, recipients, feedback, presets, symbols)
* `tests/test_firestore_memory.py`: PASSED (Profile persistence, vocabulary learning, delete profile, dynamic presets)
* `tests/test_symbol_resolver.py`: PASSED (Direct match, synonym resolution, verbs and people, text fallback, symbol search)

---

### Strategic Next Steps and Expansion Roadmap

For your AI to analyze and prioritize, here are high value roadmap directions:

1. **Progressive Web App (PWA) and Offline Service Worker**:
   * Pre cache vector SVGs and top 1,000 ARASAAC pictograms into IndexedDB so the studio operates smoothly offline in clinical or school environments with no internet.
2. **Camera and Multimodal Vision Input**:
   * Allow caregivers to snap a photo of a physical scene (*e.g., breakfast table, classroom activity, therapy room*) and have Gemini 2.5 Flash Vision automatically extract relevant AAC symbols.
3. **Switch Access and Eye Tracking Compatibility**:
   * Integrate row column scanning and assistive switch key bindings (*Spacebar, Enter, external Bluetooth switches*) for individuals with motor impairments.
4. **Multilingual Translation**:
   * Support dual language cards (*e.g., English + Spanish / French / Arabic*) enabling bilingual households and international clinics to use the platform.
5. **SLP Clinical PDF Report Export**:
   * Generate formal PDF communication tracking summaries showing vocabulary acquisition velocity and board usage trends for insurance or IEP (Individualized Education Program) reviews.
