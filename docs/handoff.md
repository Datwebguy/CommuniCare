# CommuniCare, Handoff

## Current Status
All core modules, agent orchestration pipeline, Firestore memory layer, ARASAAC symbol resolver, FastAPI backend, Docker containerization, interactive web interface, and test suites are fully built and passing.

## How to Run & Verify
1. `pip install -r requirements.txt`
2. `python -m pytest tests/ -v`
3. `python -m uvicorn communicare.main:app --port 8080`
4. Open `http://localhost:8080` in browser to test the interactive UI and the 2-Turn Adaptive Demo.
