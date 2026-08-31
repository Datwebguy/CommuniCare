# CommuniCare — step-by-step submission (Cloud Billing blocked)

Cloud Billing error `OR_BACR2_44` means you **cannot** create Cloud Run this week. That is OK.

Hackathon rules require **all three**:

1. Gemini 3.5+ (Gemini API or Vertex AI)
2. One Google agent framework — we use **Google GenAI SDK** (`google-genai`)
3. One Google Cloud service — we use **Firestore** (explicitly allowed: Cloud Run, Cloud SQL, **Firestore**, GKE, Pub/Sub)

Hosted app can stay on Vercel. The **video must show Firestore in the Google/Firebase Console**.

Official rules: [allthingsagentichackathon.devpost.com/rules](https://allthingsagentichackathon.devpost.com/rules)  
FAQs: [allthingsagentichackathon.devpost.com/details/faqs](https://allthingsagentichackathon.devpost.com/details/faqs)  
Resources: [allthingsagentichackathon.devpost.com/resources](https://allthingsagentichackathon.devpost.com/resources)

---

## Bookmark these first

| What | Link |
| --- | --- |
| Hackathon home | https://allthingsagentichackathon.devpost.com/ |
| **GEAR** (Gemini Enterprise Agent Ready) | https://developers.google.com/program/gear |
| Claim GEAR badge | https://developers.google.com/profile/badges/community/gear |
| GEAR FAQ | https://developers.google.com/profile/help/gear |
| Intro to Agents (GEAR path) | https://www.skills.google/paths/3546 |
| Google Developer Program | https://developers.google.com/program |
| Hackathon GEAR / badge page | https://g.dev/cloud/all-things-agentic |
| Gemini API / AI Studio | https://aistudio.google.com/ |
| Create Gemini API key | https://aistudio.google.com/apikey |
| Gemini docs | https://ai.google.dev/ |
| Firebase Console (Firestore lives here) | https://console.firebase.google.com/ |
| Create Firestore (opens current project) | https://console.firebase.google.com/project/_/firestore |
| Firebase service accounts | https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk |
| Firestore server setup docs | https://firebase.google.com/docs/firestore/quickstart-server |
| Firebase pricing (Spark = free, no Blaze) | https://firebase.google.com/pricing |
| Google Cloud Console | https://console.cloud.google.com/ |
| Cloud Firestore in GCP Console | https://console.cloud.google.com/firestore |
| GCP service accounts | https://console.cloud.google.com/iam-admin/serviceaccounts |
| Cloud Billing (only if you retry later) | https://console.cloud.google.com/billing |
| GCP free trial | https://cloud.google.com/free |
| Hackathon $150 credits form (may be exhausted) | https://forms.gle/5PtXmw1dSbDnpYke9 |
| Devpost Discord | https://discord.gg/HP4BhW3hnp |
| Vercel dashboard | https://vercel.com/dashboard |
| Live CommuniCare app | https://usecommunicare.vercel.app/ |
| Health check | https://usecommunicare.vercel.app/api/health |
| Caregiver Studio | https://usecommunicare.vercel.app/app |
| GitHub repo | https://github.com/Datwebguy/CommuniCare |
| YouTube Studio (upload demo) | https://studio.youtube.com/ |
| Judging Q&A recording | https://youtu.be/DCXjvKmUIGY |

---

## Step 0 — Join GEAR (5 minutes, free)

This is the hackathon on-ramp Google advertised. It does **not** create Cloud Billing. Do it so your Google Developer profile shows GEAR.

1. Open **https://developers.google.com/program/gear**
2. Click **Sign in** with the Google account you use for the hackathon.
3. If you are not in the Google Developer Program yet: **https://developers.google.com/program** → join (free).
4. Claim the badge: **https://developers.google.com/profile/badges/community/gear**
5. Optional labs: **https://www.skills.google/paths/3546** (Intro to Agents).
6. Hackathon GEAR page: **https://g.dev/cloud/all-things-agentic**

GEAR FAQ: **https://developers.google.com/profile/help/gear**

---

## Step 1 — Gemini 3.5 API key (5 minutes, free)

1. Open **https://aistudio.google.com/apikey**
2. Sign in.
3. Click **Create API key**.
4. If asked for a Google Cloud project, pick any existing project **or** “Create project”. This does **not** need Cloud Billing for the free Gemini API.
5. Copy the key. You will paste it into Vercel. Never commit it to GitHub.

Docs: **https://ai.google.dev/**

You already have a key in local `.env`. You can reuse that same key on Vercel.

---

## Step 2 — Firebase project (no Blaze, no billing)

1. Open **https://console.firebase.google.com/**
2. Click **Add project** (or open a project you already have, e.g. a Gemini / “Gemini Project 2” project).
3. Name it something like `communicare-hackathon`.
4. Google Analytics: **Off** is fine (faster).
5. Click **Create project** → **Continue**.
6. Confirm the plan is **Spark** (no-cost). Pricing: **https://firebase.google.com/pricing**
7. **Do not** click “Upgrade to Blaze”. That is the billing wall you already hit.

Copy the **Project ID** from Project settings (gear, top left). Example: `communicare-hackathon-12345`. You need this exact string later.

---

## Step 3 — Create Firestore (the required Google Cloud service)

Official create flow: **https://firebase.google.com/docs/firestore/quickstart-server**

1. In the Firebase Console left sidebar go to **Build** → **Firestore Database**, or open  
   **https://console.firebase.google.com/project/_/firestore**  
   (it will ask you to pick the project).
2. Click **Create database**.
3. If it asks Standard vs Enterprise, choose **Standard**.
4. Location: `nam5 (United States)` or `us-central1` is fine.
5. Security rules: **Start in test mode** (hackathon only; expires in 30 days, enough for judging).
6. Click **Create**. Wait until the empty data viewer appears.

You now have **Google Cloud Firestore**. You can also view the same database at  
**https://console.cloud.google.com/firestore**

If create fails and asks you to enable billing / Blaze, you picked the wrong upgrade. Stay on Spark. Use a **new Firebase project** and do not enable any paid product (Storage, Functions paid, App Hosting paid, etc.).

---

## Step 4 — Download a service account key

Firebase UI:

1. Gear (next to Project Overview) → **Project settings**.
2. Tab **Service accounts**.  
   Direct: **https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk**
3. Confirm language **Python** (or any; the JSON is the same).
4. Click **Generate new private key** → **Generate key**.
5. A `.json` file downloads. Keep it on your PC. **Do not** add it to the git repo.

Same key from Google Cloud Console:

**https://console.cloud.google.com/iam-admin/serviceaccounts**  
→ your project → the `firebase-adminsdk-…` account → **Keys** → **Add key** → **JSON**.

The JSON looks like:

```json
{
  "type": "service_account",
  "project_id": "communicare-hackathon-12345",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-...@....iam.gserviceaccount.com"
}
```

`project_id` inside the file is `GOOGLE_CLOUD_PROJECT`.

---

## Step 5 — Put secrets on Vercel (so the live site uses Gemini + Firestore)

Vercel dashboard: **https://vercel.com/dashboard**  
App (after deploy): **https://usecommunicare.vercel.app/**

1. Open the **CommuniCare** Vercel project.
2. **Settings** → **Environment Variables**  
   (URL shape: `https://vercel.com/<your-team>/<project>/settings/environment-variables`)
3. Add these four. Apply to **Production** (and Preview if you want).

| Name | Value |
| --- | --- |
| `GEMINI_API_KEY` | the key from Step 1 |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `GOOGLE_CLOUD_PROJECT` | Firebase **Project ID** from Step 2 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | **entire** service account JSON, one line |

How to paste the JSON as one line (PowerShell, in the folder that contains the downloaded key):

```powershell
Get-Content -Raw .\your-downloaded-key.json
```

Copy the whole output into the Vercel value. It must start with `{` and end with `}`.

4. **Deployments** → latest deployment → **⋯** → **Redeploy** (or push a commit). Wait until it is Ready.

Local `.env` (optional, for `localhost:8080`):

```ini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash
GOOGLE_CLOUD_PROJECT=your-firebase-project-id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

Never commit `.env` or the JSON file. `.gitignore` already blocks them.

---

## Step 6 — Prove it works (do this before recording)

### 6a. Health check

Open **https://usecommunicare.vercel.app/api/health**

You need:

```json
{
  "status": "healthy",
  "gemini_active": true,
  "gemini_model": "gemini-3.5-flash",
  "firestore_mode": "Google Cloud Firestore"
}
```

| If you see | Meaning | Fix |
| --- | --- | --- |
| `gemini_active: false` | Vercel does not have `GEMINI_API_KEY` | Step 5, then **Redeploy** |
| `firestore_mode: "Local Persistent JSON State"` | service account JSON missing/invalid | Step 4–5, paste full JSON, Redeploy |
| 404 / old site | deployment not live | Redeploy Production |

### 6b. Generate a board so Firestore gets a document

1. Open **https://usecommunicare.vercel.app/app**
2. Sign in or use the studio.
3. Select **Leo** (or create a recipient).
4. Click **Morning Routine** (or type a message) → **Generate Cards**.
5. Click **Worked Well** on **MEDICINE**.

### 6c. See it in Google Cloud / Firebase Console (judging proof)

1. **https://console.firebase.google.com/** → your project → **Firestore Database**
2. You should see collection `caregivers` → a document → subcollection `recipients` → Leo (or your recipient) with `learned_vocabulary` / `success_history`.
3. Same data in GCP: **https://console.cloud.google.com/firestore**

Screenshot/record **this screen**. That is “backend on Google Cloud.”

---

## Step 7 — Record the demo (max 4 minutes)

Upload: **https://studio.youtube.com/** (public, not unlisted) or Vimeo public. English.

Use the script in `DEMO_VIDEO_SCRIPT.md`. Mandatory shots:

1. Live app **https://usecommunicare.vercel.app/**
2. Firebase Console Firestore with real documents (Step 6c)
3. **https://usecommunicare.vercel.app/api/health** showing `gemini_active: true` and `firestore_mode: "Google Cloud Firestore"`
4. Live generate → 5-step trace → Worked Well → second message with memory badge

Do **not** wait for Cloud Run. Do **not** record only Vercel UI with no Console.

Judges’ own Q&A: **https://youtu.be/DCXjvKmUIGY**

---

## Step 8 — Submit on Devpost

1. **https://allthingsagentichackathon.devpost.com/** → **Enter a Submission** (must be registered).
2. Fill:

| Field | What to enter |
| --- | --- |
| Category | **Taskmaster** (one track only) |
| Hosted project URL | https://usecommunicare.vercel.app/ |
| Repo | https://github.com/Datwebguy/CommuniCare |
| Demo video | public YouTube/Vimeo link |
| Architecture diagram | `docs/architecture_diagram.png` in the repo |
| Technologies | Gemini 3.5 Flash, Google GenAI SDK (`google-genai`), Google Cloud Firestore |
| Data sources | ARASAAC (CC BY-NC-SA 3.0) |

**Paste this in the description (findings / learnings):**

> CommuniCare is a Taskmaster workflow: a caregiver message in, a finished AAC board out (Firestore profile → Gemini 3.5 Flash via google-genai → ARASAAC → Fitzgerald Key layout → Firestore memory).  
> Qualifying Google Cloud infrastructure: **Cloud Firestore**.  
> Cloud Run (`Dockerfile`, `cloudbuild.yaml`) is in the repo; creating a Cloud Billing account failed with **OR_BACR2_44**, so the live host is Vercel while memory and state run on Firestore. Proof is in the demo video (Firebase/Cloud Console + `/api/health`).

3. Push these local files to GitHub **before** you lock the submission:  
   **https://github.com/Datwebguy/CommuniCare**

Deadline: **31 August 2026, 5:00 PM PT**  
https://allthingsagentichackathon.devpost.com/details/dates

---

## Optional extras (bonus points)

Rules bonus: [official rules §6](https://allthingsagentichackathon.devpost.com/rules)

- Public blog/dev.to/YouTube saying you built it **for this hackathon**
- Social post with **#AllThingsAgenticHackathon**  
  Example X: https://x.com/compose
- Extra Google models (Gemma / Veo / Lyria) — skip if you are out of time

Stuck? Devpost Discord: **https://discord.gg/HP4BhW3hnp**  
Discussion board: **https://allthingsagentichackathon.devpost.com/forum_topics**

---

## Order of operations (do not skip)

1. GEAR badge — https://developers.google.com/program/gear  
2. Gemini key — https://aistudio.google.com/apikey  
3. Firebase Spark project — https://console.firebase.google.com/  
4. Create Firestore — https://console.firebase.google.com/project/_/firestore  
5. Service account JSON — https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk  
6. Vercel env + Redeploy — https://vercel.com/dashboard  
7. Check https://usecommunicare.vercel.app/api/health  
8. Generate a board, then show Firestore in the Console  
9. Record ≤ 4 min, upload https://studio.youtube.com/  
10. Submit https://allthingsagentichackathon.devpost.com/
