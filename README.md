# Cinema Commander

## HACK-CINE-012 — Live Agent Experience

Cinema Commander is a standalone Gemini + Google ADK multi-agent production intelligence control tower with real Parallel Search runtime integration.

This milestone connects the polished Control Tower UI to the actual backend agent execution. Judges can press **RUN COMMAND** and watch real Google ADK execution events stream into the browser through Server-Sent Events (SSE).

### Live workflow

```text
Director Brief
      ↓
Google ADK SequentialAgent
      ↓
Planning + Research (ParallelAgent)
      ↓
Parallel Search
      ↓
Production Intelligence
      ↓
Risk + Schedule (ParallelAgent)
      ↓
Greenlight Director
      ↓
Live SSE stream
      ↓
Control Tower
```

### Runtime stack

- Google Gemini
- Google ADK
- Google Cloud Agent Runtime compatibility
- Parallel Search API
- FastAPI
- Deterministic production intelligence, risk, schedule, and greenlight engines
- Server-Sent Events for live browser execution state

### Live APIs

- `POST /api/agent/run`
- `GET /api/agent/stream/{execution_id}`
- `GET /api/agent/run/{execution_id}`
- `POST /api/agent/analyze`
- `POST /api/research/search`
- `POST /api/research/intelligence`
- `POST /api/risk/assess`
- `POST /api/schedule/evaluate`
- `POST /api/greenlight/decide`

### Demo safety

Published screenshots/video should use the fictional/mock production corpus. The hosted application may use genuine Parallel Search results at runtime in accordance with the organizer guidance.

### License

MIT License
