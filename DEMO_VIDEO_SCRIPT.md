# CommuniCare — demo video script

**Length:** 3:30–3:55 (judges only watch the first 4 minutes)  
**Live app:** https://usecommunicare.vercel.app/  
**Studio:** https://usecommunicare.vercel.app/app  
**Health check:** https://usecommunicare.vercel.app/api/health  
**Firestore:** https://console.firebase.google.com/project/communicare-a00c9/firestore  
**GitHub:** https://github.com/Datwebguy/CommuniCare  

Record in Chrome at 100% zoom, 1920×1080, with a clear mic. Speak in a warm, steady voice. After each click, pause half a second so the action is visible.

---

## Before you record

Open three tabs and leave them loaded:

1. https://usecommunicare.vercel.app/
2. https://usecommunicare.vercel.app/api/health — confirm `"gemini_active": true` and `"firestore_mode": "Google Cloud Firestore"`
3. https://console.firebase.google.com/project/communicare-a00c9/firestore

On the studio (`/app`): sign **out** so the header shows **Sign In / Join**. Make sure a recipient named **Leo** exists (if not, sign in once, click **+** next to Recipient, add Leo as Child / Basic, then sign out). Confirm a **Morning Routine** chip is in Quick Topics. Speakers on.

If health still says `Local Persistent JSON State`, do not record.

---

## Scene 1: Problem and landing (0:00 – 0:30)

**What to do:** Start on the landing page. Keep the address bar visible (`usecommunicare.vercel.app`). Do not click Launch Studio yet. Slowly point at the four floating cards: MEDICINE, WALK, PANCAKES, HAPPY. Scroll just enough to show the line “Built with Google Cloud & Gemini 3.5 Flash.”

**What to say:**
"Hi everyone, my name is [Your Name], and this is CommuniCare. Across the world, caregivers who support nonverbal children, stroke survivors, and people on the autism spectrum still build AAC picture boards by hand. You have something ordinary to say — take your medicine, then breakfast — but first you have to simplify the language, search a symbol library, color-code the grammar, and print a sheet. That chore takes fifteen to thirty minutes, several times a day, while the person in front of you is waiting. CommuniCare is not a chatbot that talks about communication. It is an autonomous agent that finishes that chore. You type a normal caregiver message, and it hands you a ready-to-use picture board."

---

## Scene 2: Google Cloud and Gemini proof (0:30 – 1:00)

**What to do:** Switch to the health tab. Point, in order, at `gemini_active: true`, `gemini_model: gemini-3.5-flash`, `firestore_mode: Google Cloud Firestore`, and `cloud_project: communicare-a00c9`. Then switch to the Firebase Console Firestore tab. Expand `caregivers` and a recipient document if data is already there. If the tree is empty, keep talking — you will write a document after Generate Cards.

**What to say:**
"Before we open the studio, here is the required stack running live. The agent framework is the official Google GenAI SDK — the google-genai package. The model is Gemini 3.5 Flash, and you can see gemini_active is true, so this is not the offline fallback. Persistent memory is Google Cloud Firestore in project communicare-a00c9. Every care recipient has their own document: vocabulary level, success counts, and preferred symbols, isolated per caregiver. That is the Google Cloud service this submission uses."

---

## Scene 3: Launch studio and Google Sign-In (1:00 – 1:30)

**What to do:** Go back to the landing page. Click **Launch Studio →** in the top right (wine button). Wait for `/app`. Click **Sign In / Join** (Google G on the button). In the modal, click **Continue with Google**. Complete the Google account picker. Wait until **Sign In / Join** is replaced by your avatar and name.

If Google Sign-In fails: click the **Create Account** tab. Full name `Dr. Sarah Jenkins`, email, password (6+ characters), **Create Account**. Do not freeze on camera.

**What to say:**
"Let's step into the Caregiver Studio. In healthcare, patient and family data cannot live in a shared demo bucket. CommuniCare signs caregivers in with Google — one click — and then restores their private workspace from Firestore: their recipients, their profiles, their learned history. If a clinic cannot use OAuth, email signup is here as a fallback, but Google Sign-In is the path we want you to see."

---

## Scene 4: Recipients and isolation (1:30 – 2:00)

**What to do:** In the header, open the **Recipient:** dropdown. If both Leo and Maya exist, select **Maya (ADULT)** and pause so it stays selected. Then select **Leo (CHILD)**. If only Leo exists, select Leo, then click **+**, add Maya quickly (Adult, Intermediate) if you have time — otherwise stay on Leo and still say the isolation line. Point at **Quick Topics** chips (Morning Routine, Doctor & Health, School, Bedtime).

**What to say:**
"I select Maya, and she stays selected. Her data will not mix with Leo's. That matters because each person has different communication needs and vocabulary levels. Each profile has its own cognitive settings, card limit, and learned preferences — all stored separately in Firestore. We also have quick topic presets for the routines caregivers actually repeat: morning schedules, medication times, school, and bedtime."

---

## Scene 5: Board generation (2:00 – 2:30)

**What to do:** Select **Leo (CHILD)**. Click the **Morning Routine** preset. Confirm the textarea filled; if not, type: `Good morning Leo! Please take your medicine with a glass of water, then eat warm pancakes for breakfast.` Leave Style on **Core Words**. Click **⚡ Generate Cards**. Wait for the board. Point at MEDICINE, WATER, PANCAKES and the Color Guide. Click **View Details** on the Autonomous Pipeline so all five steps show completed.

**What to say:**
"Now let's create a communication board. I'll select Leo and use the morning routine preset. When I click Generate Cards, our autonomous agent pipeline executes in under a second. First, it queries Google Cloud Firestore for Leo's profile and vocabulary level. Then it calls Google Gemini 3.5 Flash using the official Google GenAI SDK to extract core intents and simplify the message. Next, it queries the ARASAAC catalog for standardized pictograms. Finally, it assembles the board using the clinical Fitzgerald Key color standard — Yellow for People, Green for Actions, Orange for Objects. In under one second, we have a ready-to-use, color-coded visual board."

---

## Scene 6: Interactive features (2:30 – 3:00)

**What to do:** Click MEDICINE, then WATER, then PANCAKES — wait for the glow and audio each time. Click **Speak All** and let the full sentence finish. Click **Voice Tone**. Change Voice Tone Persona to **Child Friendly**. Click **Preview Voice**, then **Apply Voice**, then close the modal.

**What to say:**
"Every card is interactive. Tapping a card highlights it and reads the word aloud using the browser's Web Speech API. Clicking Speak All triggers our asynchronous sequencer, vocalizing the full instruction without clipping or dropping words. Caregivers can customize voice tones to match sensory needs — like this Child Friendly persona with higher pitch and warmer tone for younger users. This flexibility is important because different individuals have different sensory sensitivities."

---

## Scene 7: Memory and learning (3:00 – 3:30)

**What to do:** Click **Worked Well** on the MEDICINE card. Wait for the toast. Optionally refresh the Firestore tab and point at Leo's document. Back in the studio, replace the message with: `Leo, remember to take your afternoon medicine before we go for a walk.` Click **Generate Cards**. Point at the purple banner: **Personalized preference applied from memory**.

**What to say:**
"What makes CommuniCare truly autonomous is persistent multi-turn memory. When I reinforce a card by clicking Worked Well, CommuniCare updates Leo's profile in Google Cloud Firestore. Later, when I enter an afternoon message about medicine, Gemini 3.5 Flash automatically cross-references his learned history and prioritizes his preferred symbols — see this badge: Personalized preference applied from memory. The agent autonomously adapts to each individual over time, learning and improving with every interaction. This means the system gets smarter with use."

---

## Scene 8: Export and closing (3:30 – 4:00)

**What to do:** Click **Print Sheet**. If the print dialog opens, show the layout, then press Esc. Click **Presentation** for fullscreen tablet mode. Pause two seconds. Press Esc or **Exit Presentation**. Click your avatar → **GitHub Repository**, or show https://github.com/Datwebguy/CommuniCare. End on the studio with the board still visible.

**What to say:**
"Caregivers can generate a one-click Printable Sheet for physical communication binders, or launch full-screen Presentation Mode on tablets for distraction-free interaction. That makes CommuniCare practical at home, in clinics, and in school. This is the Taskmaster track: a complete autonomous workflow for a messy, multi-step chore — not a chat window. We use the official Google GenAI SDK with Gemini 3.5 Flash, and Google Cloud Firestore for persistent memory. The project is open source under MIT. By combining Gemini with clinical AAC standards, we turn caregiver speech into a board you can hold up in the same breath. Thank you."

---

## If you are over time, cut in this order

1. Voice Tone preview (keep one card tap + Speak All)  
2. Print Sheet (keep Presentation)  
3. Maya switch (keep the isolation sentence on Leo)

Never cut Scene 2 (health + Firestore) or Scene 5 (generate + five steps).

## After recording

Upload **public** to YouTube: https://studio.youtube.com/  
Devpost category: **Taskmaster**  
Hosted URL: https://usecommunicare.vercel.app/  
Repo: https://github.com/Datwebguy/CommuniCare  
Description: paste from `docs/devpost-text.md`  
Say **Google GenAI SDK** in the video. Do not say Strands Agents — this repo does not use it.
