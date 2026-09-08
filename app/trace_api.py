from app.evidence import EvidenceTrace

def build_trace_demo(execution_id:str="DEMO-EXECUTION")->dict:
    trace=EvidenceTrace(execution_id)
    evidence=trace.add_evidence("https://example.com/production-access",title="Fictional Location Access Notice",snippet="Night access requires prior production authorization.",category="ACCESS",confidence=.94)
    trace.add_event("EXECUTION_STARTED","cinema_commander","Production analysis execution started.")
    trace.add_event("AGENT_STEP","production_planner","Production brief decomposed into operational workstreams.")
    trace.add_event("TOOL_CALL","research_scout","Parallel Search research initiated.")
    trace.add_event("EVIDENCE_RETRIEVED","research_scout","Production access evidence retrieved.",[evidence.evidence_id])
    trace.add_event("AGENT_STEP","risk_officer","Risk assessment evaluated production constraints.",[evidence.evidence_id],{"severity":"HIGH"})
    trace.add_event("AGENT_STEP","schedule_agent","Schedule evaluated against the shoot window.")
    trace.add_event("GREENLIGHT_EVALUATED","greenlight_director","Final production decision evaluated.",[evidence.evidence_id],{"decision":"WARNING","confidence":.88})
    return trace.export()
