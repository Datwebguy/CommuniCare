# CommuniCare, Architecture

## Overview

CommuniCare is an autonomous pipeline, not a chat interface. A caregiver message goes in, and a finished picture symbol board comes out, with no manual steps required from the caregiver in between. The system is built to satisfy the hackathon's required stack: Gemini (2.5 / 3.5 Flash), Google GenAI SDK Agent Orchestrator, and Google Cloud infrastructure (Firestore & Cloud Run), while demonstrating architectural discipline.

## High Level Flow

A caregiver submits a message. The agent receives it and executes the pipeline:
1. Recipient Profile Lookup from Firestore.
2. Language Simplification & Concept Extraction via Gemini.
3. Symbol Reasoning & Resolution via ARASAAC & local vector library with text fallbacks.
4. High-Contrast Board Composition applying the clinical Fitzgerald Key color standard.
5. Interaction & Feedback persistence back into Firestore.

## Components

- **Agent Orchestration (Google GenAI SDK Pipeline)**: Coordinates the 5 autonomous steps, handles fallback logic when concepts have no exact match.
- **Language and Reasoning (Gemini 2.5 / 3.5 Flash)**: Plain language simplification, concept extraction, and grammatical categorization.
- **Persistent Memory (Firestore)**: Stores profile documents per care recipient with learned vocabulary, symbol mappings, and interaction history.
- **Symbol Library**: Open-license AAC symbols (ARASAAC / CC BY-NC-SA) and curated vector pictograms.
- **Hosting (Cloud Run)**: Containerized deployment on Cloud Run.
- **Caregiver & Recipient Interface**: Fast, responsive web UI with Web Speech API audio, fullscreen presentation view, and print/laminated board layout.
