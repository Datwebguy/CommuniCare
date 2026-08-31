# CommuniCare — full recording script (direct this like a shoot)

You are not “showing a website.” You are proving three things in under four minutes:

1. A real caregiving chore (building AAC boards by hand).
2. An agent that **finishes** that chore (Google GenAI SDK + Gemini 3.5 Flash).
3. Google Cloud is actually in the loop (Firestore console + `/api/health`).

If you skip the Cloud proof, or mumble “AI backend,” the video fails the rubric even if the UI looks pretty.

---

## Setup (do this before Record)

**Browser:** Chrome. Window size ~1920×1080. Zoom **100%**. Hide bookmarks bar (`Ctrl+Shift+B`). Close Slack/email popups.

**Mic:** Sit close. Speak slightly slower than normal. Smile on the first line.

**Three tabs, in this order, already loaded:**

| Tab | URL | Why |
| --- | --- | --- |
| 1 | https://usecommunicare.vercel.app/ | Landing |
| 2 | https://usecommunicare.vercel.app/api/health | Gemini + Firestore proof |
| 3 | https://console.firebase.google.com/project/communicare-a00c9/firestore | Cloud proof |

**On tab 2 you must already see:**

```json
"gemini_active": true
"gemini_model": "gemini-3.5-flash"
"firestore_mode": "Google Cloud Firestore"
"cloud_project": "communicare-a00c9"
```

If `firestore_mode` is still `Local Persistent JSON State`, **do not record.** Fix env first.

**On tab 1 /app (open once, then go back to landing):**

- Sign **out** so the header shows **Sign In / Join** (not your avatar).
- Confirm a recipient named **Leo** exists. If not: Sign In once, click **+** next to Recipient, create Leo (Child, Basic), then sign out again so the login scene is clean.
- Confirm a **Morning Routine** chip exists under Quick Topics.

**Recording:** Windows Game Bar `Win+G` or OBS. 1080p. **You must talk the whole time.** Upload public YouTube: https://studio.youtube.com/ — not unlisted if you want the bonus content point.

**Hard cap:** 3 minutes 50 seconds. Judges stop at 4:00.

---

## How to use this document

Each scene has:

- **CLOCK** — when to be there
- **CAMERA** — what must be on screen
- **MOUSE** — exact control names as they appear in the app
- **YOU SAY** — read this. Do not improvise the framework names.

Move the cursor slowly. After every click, freeze 0.4 seconds so the click is visible.

---

# SCENE 1 — The problem (0:00–0:40)

**CLOCK:** 0:00  
**CAMERA:** Tab 1. Landing page. Address bar visible: `usecommunicare.vercel.app`  
**MOUSE:** Do **not** click Launch Studio. Drift the cursor across the four glass cards in this order: **MEDICINE** (top left) → **WALK** (bottom left) → **PANCAKES** (top right) → **HAPPY** (bottom right). Then rest on the headline.

**YOU SAY:**

> Hi. My name is [YOUR NAME], and this is CommuniCare.
>
> I want you to picture a real morning. You are a parent, or a speech therapist, or a home-care aide. The person in front of you does not use fluent speech. They use picture cards. You need to say something completely ordinary: “Please take your medicine with water, then eat pancakes.”
>
> Before you can say it, you have to *build the board*. Search a symbol library. Pick six pictures. Color-code people yellow and actions green. Resize. Print. Laminate. That is fifteen to thirty minutes — every routine, every day — while the person is waiting.
>
> CommuniCare is not a chatbot that talks about AAC. It is an agent that **does the chore**. You type the sentence you would have said. It hands you a finished board.

**CUT TO SCENE 2 at 0:40.** If you are still on the hero at 0:45 you are too slow. Skip the last sentence and move.

---

# SCENE 2 — Prove Google Cloud (0:40–1:05)

This is the scene people rush. Do not.

**CLOCK:** 0:40  
**CAMERA:** Switch to **Tab 2**. Zoom the browser to 125% if the JSON is small (`Ctrl` + `+` once). Cursor underlines these four fields, slowly, top to bottom.

**MOUSE:**

1. Point at `"gemini_active": true`
2. Point at `"gemini_model": "gemini-3.5-flash"`
3. Point at `"firestore_mode": "Google Cloud Firestore"`
4. Point at `"cloud_project": "communicare-a00c9"`

Then switch to **Tab 3**. Click into the Firestore data tree. Expand **caregivers** if it is there. Hover a recipient document so the judge can read field names like `learned_vocabulary` or `success_history`. If the tree is empty, say the next line anyway and keep moving — you will write a document in Scene 7.

**YOU SAY:**

> Two things the rules asked for, on screen, live.
>
> First: the agent framework is the **Google GenAI SDK** — the official `google-genai` package. The model is **Gemini 3.5 Flash**. You can see `gemini_active` is true. This is not the offline fallback.
>
> Second: the Google Cloud service is **Cloud Firestore**. Same project: `communicare-a00c9`. Every recipient’s vocabulary lives here, isolated per caregiver. That is the memory the pipeline reads before it builds a board, and writes after.

**CUT TO SCENE 3 at 1:05.** Zoom Chrome back to 100% (`Ctrl+0`) as you switch tabs so the landing is not huge.

---

# SCENE 3 — Enter the studio and Google Sign-In (1:05–1:35)

**CLOCK:** 1:05  
**CAMERA:** Tab 1, landing, 100% zoom.

**MOUSE — exact sequence:**

1. Top-right wine button: **Launch Studio →**  
   (Do not use “Try Interactive Demo.” That stays on the marketing page.)
2. Wait for `/app`. Confirm the header: left **CommuniCare / AAC Studio**, center **Recipient:**, right **✨ Adaptive Demo** and **Sign In / Join**.
3. Click **Sign In / Join** (the button with the Google G).
4. Modal title: **Sign In to CommuniCare**.
5. Click the large button **Continue with Google**.
6. In the Google popup: choose your account → Continue / Allow.
7. Wait until the header **Sign In / Join** is **gone** and your **avatar circle + name** appear on the right.

**If the Google popup is blocked:** click the browser’s popup icon in the address bar → Always allow. Retry **Continue with Google**.

**If Google Sign-In still fails (10-second backup):**

1. In the same modal, click the tab **Create Account**.
2. Full Name: `Dr. Sarah Jenkins`
3. Email: a real inbox you control, or `sarah.demo@gmail.com` if you already registered it.
4. Password: anything 6+ characters.
5. Click **Create Account**.
6. Say the backup line below. Do **not** go silent.

**YOU SAY (while clicking):**

> This is the Caregiver Studio. Patient data cannot be a shared toy box, so the first action is identity.
>
> I’m signing in with Google. One click. The agent then loads *my* workspace from Firestore — my recipients, my history — not a global demo user.

**Backup line if you used email instead:**

> Google Sign-In is the primary path. Email signup is here as a fallback so a clinic without OAuth still gets an isolated workspace.

**CUT when your name is visible in the header.** Target 1:35.

---

# SCENE 4 — Pick the person you are talking to (1:35–1:50)

**CLOCK:** 1:35  
**CAMERA:** Studio header, center.

**MOUSE:**

1. Click the **Recipient:** dropdown.
2. If **Leo** is listed, click **Leo** (or `Leo (CHILD)`).
3. If Leo is missing:
   - Click the small **+** button immediately to the right of the dropdown.
   - Modal: **Add Care Recipient Profile**.
   - Name: `Leo`
   - Age group: Child
   - Vocabulary: Basic
   - Save / create.
   - Select Leo in the dropdown.
4. Hover the **Quick Topics** row so chips are readable: Morning Routine, Doctor & Health, etc.

**YOU SAY:**

> The agent always builds for one person. Leo is a child on a basic board — fewer cards, simpler words. If I switched to an adult profile, the board would get denser. Those memories never mix. That is the Firestore isolation you just saw in the console.

**CUT at 1:50.** Do not explain every chip.

---

# SCENE 5 — One click, finished board (1:50–2:30)

This is the “money” scene. Let the board appear. Do not talk over a blank grid.

**CLOCK:** 1:50  
**CAMERA:** Composer card (textarea) then the board grid.

**MOUSE:**

1. Under **Quick Topics:** click **🌅 Morning Routine** (wording may be “Morning Routine” without emoji — click the first morning/breakfast chip).
2. Confirm the textarea filled. If it is empty, click into `#caregiver-message` and type, slowly enough to be readable:

   `Good morning Leo! Please take your medicine with a glass of water, then eat warm pancakes for breakfast.`

3. Leave **Style:** on **Core Words**. Do not open the dropdown unless you need to set it back.
4. Click **⚡ Generate Cards**.
5. **Hands off.** Wait until picture cards fill the grid (MEDICINE, WATER, PANCAKES, etc.).
6. Point at the **Plain Words:** ribbon under the title — the simplified sentence.
7. Point along the **Color Guide** pills: Yellow People, Green Actions, Orange Things & Food.
8. Scroll if needed. Click **View Details** on the grey bar **Autonomous Pipeline / Agent Execution Trace**.
9. Hover each of the five steps left to right, 1–5, as you name them.

**YOU SAY:**

> I am not searching a catalog. I am not dragging tiles. This is the message I would have said at the breakfast table.
>
> Generate Cards.
>
> *[pause until cards appear]*
>
> There. Medicine, water, pancakes — color-coded the way speech therapists already teach: yellow for people, green for actions, orange for things.
>
> Under the hood that was five steps, no extra prompts from me. One: load Leo from Firestore. Two: **Gemini 3.5 Flash**, through the **Google GenAI SDK**, cuts the sentence down to core words. Three: match pictograms from ARASAAC. Four: lay out the Fitzgerald Key board. Five: write this session back to Firestore.
>
> That is the task. The chore is done.

**CUT at 2:30.** If generate is slow, keep the last paragraph going; do not apologize.

---

# SCENE 6 — The board is usable, not a screenshot (2:30–2:55)

**CLOCK:** 2:30  
**CAMERA:** The card grid. Unmute your speakers; the demo has TTS.

**MOUSE:**

1. Click the **MEDICINE** card once. Wait for the wine-colored speaking ring and the audio.
2. Click **WATER**. Wait.
3. Click **PANCAKES**. Wait.
4. Click **Speak All** (left side of the board toolbar). Let the full sentence play. Do not cut it off.
5. Click **Voice Tone**.
6. In **Voice & Tone Settings**, open **Voice Tone Persona**.
7. Choose **🧒 Child Friendly (Warm, High Tone)**.
8. Click **🔊 Preview Voice**. Let one phrase play.
9. Click **Apply Voice**.
10. Close the modal with the **×** in the top right.

**YOU SAY:**

> A PDF of icons is not enough. The person at the table needs sound.
>
> Each card speaks when I touch it. Speak All reads the plain sentence all the way through — that used to clip; it doesn’t now.
>
> Voice Tone is for real sensory needs. Child-friendly is higher and warmer. There is also a slow, quiet setting if someone is overwhelmed. Same board, different voice.

**CUT at 2:55.** Skip Preview if you are behind; still click Child Friendly and Apply.

---

# SCENE 7 — It remembers Leo (2:55–3:25)

**CLOCK:** 2:55  
**CAMERA:** Same board, then Firestore tab, then back.

**MOUSE:**

1. On the **MEDICINE** card, find the feedback control **👍 Worked Well** (or “Worked Well” / thumbs-up). Click it. Wait for the toast that memory was updated.
2. Switch to **Tab 3** (Firestore). Click refresh in the console if needed. Open `caregivers` → your user → `recipients` → Leo (or the probe path). Point at `success_history` or `preferred_symbol_mappings` if visible.
3. Back to **Tab 1** studio.
4. Click inside the textarea. Select all (`Ctrl+A`). Delete.
5. Type:

   `Leo, remember to take your afternoon medicine before we go for a walk to the park.`

6. Click **⚡ Generate Cards**.
7. When the new board appears, point at the purple tag: **✨ Personalized preference applied from memory**.

**YOU SAY:**

> This is the difference between a generator and an agent with state.
>
> Medicine worked for Leo this morning, so I mark Worked Well. That write goes to Firestore — you can see the document update.
>
> Afternoon, different sentence: medicine, then a walk. I do not rebuild his vocabulary by hand. The pipeline reads what already worked and tags the board: personalized preference applied from memory.
>
> Tomorrow’s board is not a stranger. It is Leo.

**CUT at 3:25.** If the purple tag does not show, still say the Firestore sentence and move to print. Do not debug on camera.

---

# SCENE 8 — Give them something they can hold (3:25–3:50)

**CLOCK:** 3:25  
**CAMERA:** Toolbar on the board.

**MOUSE:**

1. Click **Print Sheet**. If the browser print dialog opens, wait one beat so the layout is visible, then press **Esc**. Do not actually print.
2. Click **Presentation**. The board goes fullscreen. Hold two seconds. Move the cursor to a card so it is obvious this is the tablet view.
3. Click **Exit Presentation (Esc)** or press **Esc**.
4. Click your **avatar / name** in the top right.
5. In the dropdown, click **⭐ GitHub Repository**. Let the repo load, or hover the link so `github.com/Datwebguy/CommuniCare` is readable.
6. End on the studio with the board still showing. Address bar: `usecommunicare.vercel.app/app`.

**YOU SAY:**

> Last mile: a physical sheet for a binder, or fullscreen on a tablet at the table. No extra export tool.
>
> The code is public, MIT licensed: Datwebguy slash CommuniCare. Clone it, put in a Gemini key, it runs.
>
> CommuniCare: **Google GenAI SDK**, **Gemini 3.5 Flash**, **Cloud Firestore**. A caregiver message in. A finished communication board out. The thirty-minute chore is gone.
>
> Thank you.

**STOP talking by 3:50.** Fade out. Do not add “any questions.”

---

## If you are running long — cut in this order

1. Drop Voice Tone preview (keep one card click + Speak All).
2. Drop Print Sheet (keep Presentation).
3. Drop Firestore refresh in Scene 7 (keep Worked Well + second generate).
4. **Never** cut Scene 2 (health + Firestore) or Scene 5 (generate + five steps).

## If you are running short — add only this

Avatar menu → **🧠 Recipient Memory**. Point at learned vocabulary counts. One sentence: “This is the Firestore profile the next board will read.”

---

## Words you must say (checklist)

Say each of these out loud at least once:

- [ ] “Not a chatbot”
- [ ] “Google GenAI SDK”
- [ ] “Gemini 3.5 Flash”
- [ ] “Cloud Firestore”
- [ ] “Fitzgerald Key” or “yellow people, green actions”
- [ ] “Worked Well” / “memory”

Do **not** say: Strands Agents (this repo does not use it). Do **not** say “we used AI to build the backend” without naming the SDK.

---

## After you stop recording

1. Watch the first 4 minutes. If Cloud proof is missing, re-record Scene 2 and splice, or re-record the whole thing — splicing is fine if the join is clean.
2. Upload **Public** to YouTube: https://studio.youtube.com/
3. Devpost:
   - Category: **Taskmaster**
   - Hosted URL: https://usecommunicare.vercel.app/
   - Repo: https://github.com/Datwebguy/CommuniCare
   - Description: paste `docs/devpost-text.md`
4. GitHub About (repo ⚙️): description `Caregiver speech → AAC boards. Google GenAI SDK + Gemini 3.5 Flash + Firestore.` Tick **MIT** now that `LICENSE` is on `main`.
