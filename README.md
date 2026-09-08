# Cinema Commander

**AI Production Control Tower for the Agentic Cinema hackathon.**

Cinema Commander is a standalone Gemini + Google ADK multi-agent system that researches real-world production constraints through Parallel Search, converts evidence into production intelligence, evaluates risk and schedule feasibility, and produces an auditable **GREENLIGHT, WARNING, or BLOCKED** decision.

## Workflow

```text
Director Brief
      ↓
Google ADK SequentialAgent
      ↓
Planning + Research (ParallelAgent)
      ↓
Parallel Search API
      ↓
Production Intelligence
      ↓
Risk + Schedule (ParallelAgent)
      ↓
Greenlight Director
      ↓
Evidence / Execution Trace
      ↓
Live SSE Control Tower
```

## Why it is agentic

The system uses specialized Gemini agents with explicit responsibilities rather than a single chatbot:

- **Production Planner** — extracts operational constraints.
- **Research Scout** — performs runtime research through Parallel Search.
- **Production Intelligence** — structures evidence into cinema-specific findings.
- **Risk Officer** — produces an evidence-linked risk register.
- **Schedule Agent** — verifies timing and conflicts deterministically.
- **Greenlight Director** — produces the final production decision.

## Technology

- Google Gemini
- Google ADK
- Google Cloud / Vertex AI compatibility
- Parallel Search API (`parallel-web`)
- Python 3.11+
- FastAPI
- Server-Sent Events (SSE)
- Deterministic risk, schedule, intelligence, and greenlight engines

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set these values in `.env`:

```env
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GEMINI_MODEL=gemini-3.5-flash
PARALLEL_API_KEY=YOUR_PARALLEL_API_KEY
```

Authenticate Google Cloud Application Default Credentials:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Run locally:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.

## Live APIs

- `POST /api/agent/run`
- `GET /api/agent/stream/{execution_id}`
- `GET /api/agent/run/{execution_id}`
- `POST /api/agent/analyze`
- `POST /api/research/search`
- `POST /api/research/intelligence`
- `POST /api/risk/assess`
- `POST /api/schedule/evaluate`
- `POST /api/greenlight/decide`

## Demo safety

Published screenshots/video should use the fictional/mock production corpus. The hosted application may use genuine Parallel Search results at runtime in accordance with organizer guidance.

## License

MIT License. See `LICENSE`.
