# CommuniCare demo — what to say, where to click

**Length:** 3:30–3:55 (only the first 4 minutes are judged)  
**Live app:** https://usecommunicare.vercel.app/  
**Studio:** https://usecommunicare.vercel.app/app  
**Health (proof):** https://usecommunicare.vercel.app/api/health  
**Firestore (proof):** https://console.firebase.google.com/project/communicare-a00c9/firestore  
**Repo:** https://github.com/Datwebguy/CommuniCare  

Record in Chrome, 1920×1080, 100% zoom, mic on. Speak like you are showing a colleague, not reading a spec. Pause half a second after each click.

If Google Sign-In pops a window, finish it on camera. If it fails, use **Create Account** with a demo email — do not freeze.

---

## Before you hit record

1. Open three tabs and leave them ready:
   - Tab A: https://usecommunicare.vercel.app/
   - Tab B: https://usecommunicare.vercel.app/api/health
   - Tab C: https://console.firebase.google.com/project/communicare-a00c9/firestore
2. Confirm health shows `"gemini_active": true` and `"firestore_mode": "Google Cloud Firestore"`.
3. Sign **out** of the studio so the Sign In flow is visible.
4. Close extra windows. Hide bookmarks if they clutter the bar.

---

## Timing

| Time | Scene | You are looking at |
| --- | --- | --- |
| 0:00–0:35 | Problem and intro | Landing page hero |
| 0:35–0:55 | Google Cloud proof | Health JSON + Firestore console |
| 0:55–1:25 | Google Sign-In | Studio → Sign In / Join → Continue with Google |
| 1:25–1:45 | Workspace | Recipient dropdown, Leo |
| 1:45–2:25 | Generate a board | Morning Routine → Generate Cards → pipeline |
| 2:25–2:50 | Speak and voice | Cards, Speak All, Voice Tone |
| 2:50–3:20 | Memory | Worked Well → second message |
| 3:20–3:50 | Print, present, close | Print Sheet, Presentation, GitHub |

---

## Scene 1 — Introduction (0:00–0:35)

**Click:** Tab A. Stay on the landing page. Slowly pan the four floating cards: MEDICINE, WALK, PANCAKES, HAPPY. Do not click Launch Studio yet.

**Say:**

> Hi — I’m [Your Name], and this is CommuniCare.
>
> If you care for someone who is nonverbal — a child, someone recovering from a stroke, someone on the autism spectrum — you already know the morning grind. You have something ordinary to say: take your medicine, then breakfast. But they need picture cards. So you hunt a symbol library, resize tiles, color-code grammar, print a sheet. Fifteen to thirty minutes. Every routine. Every day.
>
> CommuniCare is an agent, not a chatbot. You type the sentence you would have said out loud. It builds the board.

---

## Scene 2 — Proof it runs on Google Cloud (0:35–0:55)

This shot is required. Do not skip it.

**Click:**

1. Tab B — health. Point at `gemini_active: true`, `gemini_model: gemini-3.5-flash`, `firestore_mode: Google Cloud Firestore`, `cloud_project: communicare-a00c9`.
2. Tab C — Firestore. Expand `caregivers` if documents already exist. If the tree is empty, that is fine; you will fill it in Scene 6 and glance back.

**Say:**

> Reasoning is Gemini 3.5 Flash through the Google GenAI SDK — the `google-genai` package. Memory is Google Cloud Firestore. You can see the live health check, and the same project in the Firebase console. That is the Cloud service this build uses.

---

## Scene 3 — Open the studio and sign in with Google (0:55–1:25)

**Click:**

1. Back to Tab A.
2. Top right: **Launch Studio →** (wine button). Or the hero button **Open Caregiver Studio**.
3. You land on `/app`. Top right: **Sign In / Join** (Google G on the button).
4. In the modal, click **Continue with Google**.
5. Pick your Google account. Allow.
6. Wait until the header shows your name and avatar instead of Sign In / Join.

If Google Sign-In errors: click **Create Account**, fill Full Name, Email, Password, **Create Account**. Keep talking — “email signup is the fallback; Google is the one-click path.”

**Say:**

> This is the Caregiver Studio. Workspaces are private. I’m signing in with Google so the agent can load my recipients from Firestore — not a shared demo bucket.

---

## Scene 4 — Recipient workspace (1:25–1:45)

**Click:**

1. Header, middle: **Recipient:** dropdown.
2. Select **Leo** if he is there.
3. If the list is empty: click the **+** next to the dropdown. Fill a name (Leo), age group Child, vocabulary Basic. Save. Select Leo.
4. Glance at **Quick Topics** chips under the composer (Morning Routine, Doctor & Health, etc.).

**Say:**

> Each person has their own profile — how many cards they can handle, which words have worked before. Leo is a child on a basic board. Maya, if she’s in the list, is a different person with a different memory. They never mix.

---

## Scene 5 — Generate the board (1:45–2:25)

**Click:**

1. Under **Quick Topics**, click **🌅 Morning Routine** (or the morning chip). The textarea should fill.
2. If it does not, type:

   `Good morning Leo! Please take your medicine with a glass of water, then eat warm pancakes for breakfast.`

3. Leave Style on **Core Words**.
4. Click **⚡ Generate Cards**.
5. Wait for the grid. Point at yellow / green / orange cards.
6. Click **View Details** on **Autonomous Pipeline** so the five steps light up: Memory Lookup, Gemini Simplification, Symbol Resolution, Board Assembly, State Persistence.

**Say:**

> I am not picking symbols. I am not dragging tiles. One click, and the pipeline runs.
>
> It loads Leo from Firestore. Gemini 3.5 Flash, via the Google GenAI SDK, turns that long sentence into a few core words. We match pictograms from ARASAAC. We lay them out on the Fitzgerald Key — yellow for people, green for actions, orange for things. Then we write the session back to Firestore.
>
> That board used to take a caregiver half an hour. This is the task the agent finishes.

---

## Scene 6 — Sound and voice (2:25–2:50)

**Click:**

1. Click the **MEDICINE** card. Wait for the glow and the spoken word.
2. Click **WATER**, then **PANCAKES**.
3. Click **Speak All**. Let the sentence finish.
4. Click **Voice Tone**.
5. Change **Voice Tone Persona** to **🧒 Child Friendly**. Click **🔊 Preview Voice**. Click **Apply Voice**. Close the modal.

**Say:**

> Every card speaks. Speak All reads the plain sentence so the person can hear it, not just see it. Voice Tone is for sensory needs — a warmer child voice, or slower and calmer if that is what they need.

---

## Scene 7 — Memory (2:50–3:20)

**Click:**

1. On the MEDICINE card, click **👍 Worked Well** (or the clear / worked-well control on the card). Wait for the toast.
2. Optional: Tab C, refresh Firestore, point at the updated document.
3. Back on the studio. Clear the textarea. Type:

   `Leo, remember to take your afternoon medicine before we go for a walk to the park.`

4. Click **⚡ Generate Cards**.
5. Point at the purple tag: **✨ Personalized preference applied from memory**.

**Say:**

> When a symbol actually works, I mark it. That preference is stored in Firestore. The next message — afternoon medicine, then a walk — the agent already knows what Leo understands. It is not a blank chat every time. It is the same person, remembered.

---

## Scene 8 — Print, present, close (3:20–3:50)

**Click:**

1. **Print Sheet** — show the printable layout, then cancel print if a dialog opens (Esc).
2. **Presentation** — fullscreen board. Pause. **Exit Presentation** or Esc.
3. Click your name (avatar pill) → **⭐ GitHub Repository** or show https://github.com/Datwebguy/CommuniCare in the bar.
4. End on the live app URL.

**Say:**

> You can print the sheet for a binder, or go fullscreen on a tablet at the table.
>
> CommuniCare is open source. Google GenAI SDK, Gemini 3.5 Flash, Cloud Firestore. A caregiver message in. A finished communication board out.
>
> Thank you.

---

## If you still have 10 seconds

Avatar menu → **🔐 Google Authenticator (2FA)** — show the setup screen, do not stall on QR.  
Or **🧠 Recipient Memory** — show learned vocabulary counts.

---

## Recording notes

- Name **Google GenAI SDK** and **Gemini 3.5 Flash** out loud in Scene 2. Judges look for the required framework early.
- Name **Firestore** while the console is on screen.
- Do not say “chatbot.” Say “agent” and “pipeline.”
- Do not record a silent screen. Narrate every click.
- If a generate is slow, keep talking: “This is the live Gemini call, not the offline fallback.”
- Upload **public** YouTube or Vimeo, English, under 4 minutes: https://studio.youtube.com/

## After recording — Devpost fields

Paste the text in `docs/devpost-text.md`.  
Hosted URL: https://usecommunicare.vercel.app/  
Repo: https://github.com/Datwebguy/CommuniCare  
Category: **Taskmaster**
