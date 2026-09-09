from __future__ import annotations
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Any
from .agent import adk_app
from .orchestration import ExecutionTrace, create_trace
from .parallel_search import ParallelSearchService
from .intelligence import build_production_intelligence
from .risk import assess_risks
from .schedule import build_schedule
from .greenlight import decide_greenlight

AGENT_NAMES = ["production_planner", "research_scout", "production_intelligence", "risk_officer", "schedule_agent", "greenlight_director"]

def _event_text(event: Any) -> str:
    if hasattr(event, "model_dump"):
        data = event.model_dump(mode="json"); content = data.get("content") or {}; parts = content.get("parts") if isinstance(content, dict) else None
        if parts:
            texts = [p.get("text") for p in parts if isinstance(p, dict) and p.get("text")]
            if texts: return "\n".join(texts)
        return str(data)
    return str(event)

def _agent_name(event: Any) -> str | None: return getattr(event, "author", None)

def _exception_details(exc: BaseException) -> str:
    if isinstance(exc, BaseExceptionGroup):
        return "\n".join([f"{type(exc).__name__}: {exc}"] + [f"  {type(x).__name__}: {x}" for x in exc.exceptions])
    return f"{type(exc).__name__}: {exc}"

def _schedule_dict(plan):
    return {"status":plan.status.value,"blocks":[{"name":b.name,"start":b.start.isoformat(),"end":b.end.isoformat(),"duration_minutes":b.duration_minutes,"status":b.status,"notes":b.notes} for b in plan.blocks],"conflicts":[{"constraint":c.constraint,"severity":c.severity,"message":c.message,"affected_blocks":c.affected_blocks,"source_urls":c.source_urls} for c in plan.conflicts],"buffer_minutes":plan.buffer_minutes,"utilization_percent":plan.utilization_percent,"assumptions":plan.assumptions,"recommendations":plan.recommendations}

async def execute_production_brief(brief: str) -> tuple[ExecutionTrace, list[dict]]:
    execution_id = str(uuid.uuid4()); trace = create_trace(execution_id); trace.begin(); events: list[dict] = []
    try:
        evidence = ParallelSearchService().search(objective=f"Find real-world production constraints for this film brief: {brief}",search_queries=[f"film production permits location access {brief}",f"film production operating hours logistics waterfront night shoot {brief}",f"film production weather safety environmental constraints {brief}"],max_results=8)
        intelligence = build_production_intelligence(brief, evidence).to_dict()
        risk = assess_risks(brief, intelligence["findings"]).to_dict()
        shoot_start = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0); shoot_end = shoot_start + timedelta(hours=6)
        schedule_dict = _schedule_dict(build_schedule(shoot_start, shoot_end,[("Crew call and safety briefing",30),("Camera and lighting setup",45),("Night confrontation shoot",180)],buffer_minutes=20))
        decision = decide_greenlight(risk, schedule_dict, intelligence.get("limitations", [])).to_dict()
        events.append({"author":"parallel_search","text":f"Retrieved {len(evidence)} live evidence sources from Parallel Search.","event":{"type":"PARALLEL_SEARCH","count":len(evidence),"evidence":evidence}})
        context=f"PRODUCTION BRIEF:\n{brief}\n\nPARALLEL SEARCH EVIDENCE:\n{evidence}\n\nPRODUCTION INTELLIGENCE:\n{intelligence}\n\nRISK ASSESSMENT:\n{risk}\n\nSCHEDULE:\n{schedule_dict}\n\nFINAL DETERMINISTIC DECISION:\n{decision}\n\nReview this supplied runtime context for your assigned role. Do not call external tools or invent facts."
        async for event in adk_app.async_stream_query(user_id="hackathon-demo-user",message=context):
            author=_agent_name(event); text=_event_text(event); raw=event.model_dump(mode="json") if hasattr(event,"model_dump") else {"event":str(event)}
            if author in AGENT_NAMES: events.append({"author":author,"text":text,"event":raw})
        for name in AGENT_NAMES:
            step=next(s for s in trace.steps if s.name==name); step.start(); role_text=next((x["text"] for x in events if x.get("author")==name),"Workflow stage completed against supplied runtime context."); step.complete(role_text)
        trace.result={"evidence_count":len(evidence),"evidence":evidence,"intelligence":intelligence,"risk":risk,"schedule":schedule_dict,"decision":decision}
        trace.finish(); return trace,events
    except Exception as exc:
        trace.fail(); details=_exception_details(exc); print("CINEMA_COMMANDER_FAILURE",details,flush=True); traceback.print_exc(); events.append({"error":str(exc),"details":details,"traceback":traceback.format_exc()}); return trace,events
