from __future__ import annotations
import uuid
from typing import Any
from .agent import adk_app
from .orchestration import ExecutionTrace,create_trace

def _event_text(event:Any)->str:
    if hasattr(event,"model_dump"):
        data=event.model_dump(mode="json"); content=data.get("content") or {}; parts=content.get("parts") if isinstance(content,dict) else None
        if parts:
            texts=[p.get("text") for p in parts if isinstance(p,dict) and p.get("text")]
            if texts:return "\n".join(texts)
        return str(data)
    return str(event)

def _agent_name(event:Any)->str|None:return getattr(event,"author",None)
async def execute_production_brief(brief:str)->tuple[ExecutionTrace,list[dict]]:
    execution_id=str(uuid.uuid4()); trace=create_trace(execution_id); trace.begin(); events=[]
    try:
        async for event in adk_app.async_stream_query(user_id="hackathon-demo-user",message=brief):
            author=_agent_name(event); text=_event_text(event); raw=event.model_dump(mode="json") if hasattr(event,"model_dump") else {"event":str(event)}
            events.append({"author":author,"text":text,"event":raw})
            if author:
                for step in trace.steps:
                    if step.name==author:
                        if step.status=="PENDING":step.start()
                        step.complete(text)
        trace.finish(); return trace,events
    except Exception as exc:
        trace.fail(); events.append({"error":str(exc)}); return trace,events
