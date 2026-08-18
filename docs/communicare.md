# CommuniCare

This file tracks the build plan, architecture, and progress for CommuniCare, the project being submitted to the All Things Agentic Hackathon by Google, under the Taskmaster track. Hackathon link: https://allthingsagentichackathon.devpost.com/

## What It Is

CommuniCare transforms everyday caregiver messages into simple words and high contrast picture symbol boards, helping caregivers communicate with people who are nonverbal or have limited speech. The chore being automated is the manual, repeated work of simplifying language and picking appropriate symbols every time a caregiver needs to communicate something, work that is slow and mentally taxing across a busy caregiving day. CommuniCare removes that translation step by autonomously watching for incoming messages or care notes and turning them into ready to use picture boards without the caregiver doing the conversion by hand each time.

## Track Fit

Entered under the Taskmaster track, which asks for a complete workflow agent rather than a chatbot, one that takes real action on a real, messy, multi step chore. CommuniCare fits this by being framed as an autonomous background pipeline, receiving a message and producing a finished, personalized communication board without requiring the caregiver to manually build it each time. Note that the underlying concept could also fit the Collaborative Partner track if reframed around live, step by step guidance, but the current build plan targets Taskmaster specifically.

## Required Technology

Every submission must use Gemini 3.5 or newer through the Gemini API or Vertex AI, at least one Google Agent Framework such as ADK, GenAI SDK, Antigravity SDK, or GenKit, and at least one Google Cloud infrastructure service such as Cloud Run, Cloud SQL, Firestore, GKE, or Pub/Sub. CommuniCare's planned stack:

Gemini 3.5 Flash handles two jobs, simplifying an incoming message into short plain language, and reasoning about which concepts in that message map to which picture symbols.

Google ADK orchestrates the agent pipeline end to end: receive message, simplify text, select symbols, assemble the board, deliver it.

Firestore stores a profile per care recipient, tracking known vocabulary, symbol preferences, and what has worked before, so the board genuinely personalizes and improves over repeated use rather than resetting each time.

Cloud Run hosts the agent service and satisfies the required Google Cloud infrastructure component, and gives a clean way to prove deployment in the demo video.

## Symbol Sourcing

Picture symbols must not be pulled from generic web image search due to copyright risk in the submission. Plan to use an open license AAC symbol set such as ARASAAC or Mulberry Symbols, or generate simple icon style pictograms directly. This decision needs to be made early since it shapes the data pipeline.

## Judging Alignment

Innovation and Operational Utility, 40 percent of the score, rewards autonomous, high value action with little hand-holding. CommuniCare's core value proposition, removing a real, repeated caregiving burden without the caregiver having to ask each time, maps directly onto this.

Architectural Discipline and Tech Stack, 30 percent, rewards decoupled systems, real state and memory management, secured credentials, and failure handling. The Firestore-backed personalization layer and the multi-step ADK pipeline are the places to demonstrate this.

Demo and Production Readiness, 30 percent, rewards a live, unedited demo, a clean architecture diagram, a reproducible README, and visible proof the project runs on Google Cloud.

## Build Timeline

Today is August 18, 2026. The submission deadline is August 31, 2026, at 5:00 PM PDT, giving 13 days.

Days 1 to 2, August 16 to 18: sign up for the free Google Cloud trial, claim the $150 in Google Cloud credits from the hackathon Resources tab, set up ADK following the beginner guide, and finalize the symbol set decision, ARASAAC, Mulberry, or generated icons.

Days 3 to 8, August 19 to 24: build the core agent pipeline end to end on a small set of real example messages. Get message in, simplified text out, symbols selected, board assembled, working before adding polish. Wire in Cloud Run.

Days 9 to 11, August 25 to 27: harden the build. Add failure handling, secure credentials properly, and implement the Firestore personalization layer so the board improves across repeated messages for the same care recipient.

Days 12 to 13, August 28 to 29: write the architecture diagram, write the README with full spin up instructions, and record the roughly 4 minute demo video. The video should show a real, unedited before and after: a real sentence goes in, a board that would normally take minutes to build by hand appears automatically, and ideally a second message shows the system adapting based on something it learned from the first.

Days 14 to 15, August 30 to 31: buffer for submission issues, plus optional bonus points, a public build journey post stating it was made for this hackathon, or a social post tagged with the hackathon hashtag.

## Submission Checklist

Category selection on Devpost.
URL to a hosted, working project, strongly encouraged though not strictly required.
Text description covering features, functionality, technologies used, other data sources, and findings.
Public or private code repository with a README containing step by step spin up instructions. If private, shared with testing@devpost.com and cloudhackathons@google.com.
Architecture diagram showing how Gemini, the ADK pipeline, Firestore, and Cloud Run connect.
Demo video, about 4 minutes, showing the problem, the value proposition, a live demo, and proof the backend runs on Google Cloud.
