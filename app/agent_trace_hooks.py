from typing import Any
from app.evidence import EvidenceTrace

def record_agent_event(trace:EvidenceTrace,agent_name:str,summary:str,data:dict[str,Any]|None=None)->None: trace.add_event("AGENT_STEP",agent_name,summary,data=data or {})
def record_tool_event(trace:EvidenceTrace,tool_name:str,summary:str,evidence_ids:list[str]|None=None,data:dict[str,Any]|None=None)->None: trace.add_event("TOOL_CALL",tool_name,summary,evidence_ids or [],data or {})
