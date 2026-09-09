from __future__ import annotations

import traceback
import uuid
from typing import Any

from .agent import adk_app
from .orchestration import ExecutionTrace, create_trace
from .parallel_search import ParallelSearchService


def _event_text(event: Any) -> str:
    if hasattr(event, "model_dump"):
        data = event.model_dump(mode="json")
        content = data.get("content") or {}
        parts = content.get("parts") if isinstance(content, dict) else None
        if parts:
            texts = [p.get("text") for p in parts if isinstance(p, dict) and p.get("text")]
            if texts:
                return "\n".join(texts)
        return str(data)
    return str(event)


def _agent_name(event: Any) -> str | None:
    return getattr(event, "author", None)


def _exception_details(exc: BaseException) -> str:
    details: list[str] = []

    def walk(error: BaseException, depth: int = 0) -> None:
        prefix = "  " * depth
        if isinstance(error, BaseExceptionGroup):
            details.append(f"{prefix}{type(error).__name__}: {error}")
            for child in error.exceptions:
                walk(child, depth + 1)
        else:
            details.append(f"{prefix}{type(error).__name__}: {error}")

    walk(exc)
    return "\n".join(details)


async def execute_production_brief(brief: str) -> tuple[ExecutionTrace, list[dict]]:
    execution_id = str(uuid.uuid4())
    trace = create_trace(execution_id)
    trace.begin()
    events: list[dict] = []

    try:
        # HACK-CINE-015: call Parallel directly so ADK never has to invoke a Python
        # function through its automatic function-calling path.
        search = ParallelSearchService()
        evidence = search.search(
            objective=f"Find real-world production constraints for this film brief: {brief}",
            search_queries=[
                f"film production permits location access {brief}",
                f"film production operating hours logistics waterfront night shoot {brief}",
                f"film production weather safety environmental constraints {brief}",
            ],
            max_results=8,
        )
        evidence_text = "\n".join(
            f"- {item['title']} | {item['url']} | {item.get('excerpt','')}"
            for item in evidence
        ) or "No Parallel Search evidence was returned."
        workflow_message = (
            f"PRODUCTION BRIEF:\n{brief}\n\n"
            f"LIVE PARALLEL SEARCH EVIDENCE:\n{evidence_text}\n\n"
            "Use this evidence throughout the workflow. Do not invent facts. "
            "The final decision must distinguish evidence gaps from confirmed constraints."
        )
        events.append({
            "author": "parallel_search",
            "text": f"Retrieved {len(evidence)} live evidence sources from Parallel Search.",
            "event": {"type": "EVIDENCE_RETRIEVED", "count": len(evidence), "evidence": evidence},
        })

        async for event in adk_app.async_stream_query(
            user_id="hackathon-demo-user",
            message=workflow_message,
        ):
            author = _agent_name(event)
            text = _event_text(event)
            raw = event.model_dump(mode="json") if hasattr(event, "model_dump") else {"event": str(event)}
            events.append({"author": author, "text": text, "event": raw})
            if author:
                for step in trace.steps:
                    if step.name == author:
                        if step.status == "PENDING":
                            step.start()
                        step.complete(text)

        trace.finish()
        return trace, events

    except Exception as exc:
        trace.fail()
        details = _exception_details(exc)
        print("CINEMA_COMMANDER_ADK_FAILURE", flush=True)
        print(details, flush=True)
        print("CINEMA_COMMANDER_ADK_TRACEBACK", flush=True)
        traceback.print_exc()
        events.append({"error": str(exc), "details": details, "traceback": traceback.format_exc()})
        return trace, events
