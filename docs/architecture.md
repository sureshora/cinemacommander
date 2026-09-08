# Architecture

```text
Director Brief
     |
     v
Google ADK SequentialAgent
     |
     +--> ParallelAgent: Production Planner + Research Scout
     |                         |
     |                         +--> Parallel Search API
     |
     +--> Production Intelligence
     |
     +--> ParallelAgent: Risk Officer + Schedule Agent
     |
     +--> Greenlight Director
     |
     v
Evidence / Trace + SSE
     |
     v
Cinema Commander Control Tower
```

## Design principle

Gemini agents handle interpretation, research planning, evidence reasoning, and executive synthesis. Deterministic application engines handle risk scoring, schedule arithmetic, evidence trace integrity, and greenlight gates. This separation improves auditability and prevents the model from being the sole authority for arithmetic or decision thresholds.

## Partner integration

The Research Scout calls Parallel Search at runtime through the official Python SDK. Search evidence is normalized and preserved with source URLs before downstream intelligence and risk analysis.

## Live execution

`POST /api/agent/run` starts a backend ADK execution. `GET /api/agent/stream/{execution_id}` exposes normalized execution events over Server-Sent Events. The browser is a view of backend execution state, not the execution engine.
