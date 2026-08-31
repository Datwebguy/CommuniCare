# Devpost submission copy (paste as-is)

This project does **not** use AWS Strands Agents. The All Things Agentic rules ask you to name the **Google** agent framework. Name **Google GenAI SDK (`google-genai`)** in the first screen of the description. Do not write “Strands Agents” unless you actually added that SDK.

Set GitHub About: add the MIT `LICENSE` file on `main` (GitHub will show License: MIT). Description: `Caregiver speech → AAC picture boards. Gemini 3.5 Flash + Google GenAI SDK + Firestore.`

---

## Short tagline (project name subtitle)

Caregiver speech in. A finished AAC picture board out.

---

## Text description (paste into Devpost)

**The problem**

Families and clinicians who support nonverbal people still build communication boards by hand. A parent wants to say something ordinary — take your medicine, then pancakes — and first has to simplify the language, search a symbol catalog, color-code grammar, and print a sheet. That chore eats 15 to 30 minutes, several times a day, at the exact moments when the person in front of them needs to understand *now*.

**Who it is for**

Primary user: the caregiver (parent, aide, SLP, teacher).  
The person who benefits: a child, teen, or adult who uses AAC picture symbols instead of fluent speech.

**What CommuniCare does**

CommuniCare is a Taskmaster agent, not a chatbot. The caregiver types or pastes a normal message. The agent returns a high-contrast picture board they can show, speak aloud, present on a tablet, or print. It remembers which symbols worked for *this* recipient and uses that memory the next time.

**How it works (Google GenAI SDK)**

The agent is orchestrated with the **Google GenAI SDK (`google-genai`)**. **Gemini 3.5 Flash** simplifies the message and extracts a small set of core concepts. **Google Cloud Firestore** stores per-caregiver, per-recipient profiles (vocabulary level, success counts, preferred symbols). Pictograms come from the open **ARASAAC** catalog plus local vector icons, laid out on the clinical **Fitzgerald Key** (yellow people, green actions, orange objects, and so on).

Pipeline, in order:

1. Look up the recipient in Firestore  
2. Simplify and extract concepts with Gemini 3.5 Flash via Google GenAI SDK  
3. Resolve symbols (ARASAAC + vectors, with text fallback)  
4. Assemble the board  
5. Write usage back to Firestore  

Live app: https://usecommunicare.vercel.app/  
Health (Gemini + Firestore): https://usecommunicare.vercel.app/api/health  
Source: https://github.com/Datwebguy/CommuniCare  

Cloud Run (`Dockerfile`, `cloudbuild.yaml`) is in the repo. Cloud Billing account creation failed with `OR_BACR2_44`, so production is on Vercel with **Firestore** as the required Google Cloud infrastructure service. The demo video shows the Firebase / Cloud Console and a live health check with `gemini_active: true` and `firestore_mode: "Google Cloud Firestore"`.

**Built with**

- Google GenAI SDK (`google-genai`) — required agent framework  
- Gemini 3.5 Flash — via Gemini API  
- Google Cloud Firestore — required Cloud service (memory)  
- FastAPI, ARASAAC (CC BY-NC-SA 3.0), Web Speech API  

**AI tools while building**

AI coding assistants were used to scaffold, debug, and write docs. The agent behavior, Firestore model, and demo are the real running system — not a mocked UI.

**Findings**

A complete AAC board is a better “action” than another chat reply: the caregiver leaves with something they can hold up. Persistent Firestore memory is what makes the second message feel like the same person, not a reset. Pretty-printed service-account JSON in Vercel env vars truncates; base64 (`GOOGLE_SERVICE_ACCOUNT_B64`) is reliable.

---

## Features (optional Devpost field)

- Natural-language caregiver input → AAC board in one request  
- Google Sign-In and optional Google Authenticator 2FA  
- Isolated recipient profiles and learned vocabulary in Firestore  
- Fitzgerald Key color coding  
- Speak card / Speak All / voice personas  
- Print sheet and fullscreen presentation  
- Caregiver “Worked Well” feedback loop  

## Technologies used

Python, FastAPI, Google GenAI SDK (`google-genai`), Gemini 3.5 Flash, Google Cloud Firestore, ARASAAC, Web Speech API, Vercel (host), Cloud Run files in repo.

## Other data sources

ARASAAC pictogram API (Government of Aragón / Sergio Palao, CC BY-NC-SA 3.0). No web image search.

## Spin-up (also in README)

```bash
git clone https://github.com/Datwebguy/CommuniCare.git
cd CommuniCare
python -m venv venv
# Windows: .\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then set GEMINI_API_KEY
python -m uvicorn communicare.main:app --host 0.0.0.0 --port 8080
```

Open http://localhost:8080/ and http://localhost:8080/app  
Tests: `python -m pytest tests/ -v`  
License: MIT (`LICENSE` in the repo root).
