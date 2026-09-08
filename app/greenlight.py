from __future__ import annotations
from dataclasses import asdict,dataclass,field
from typing import Any
@dataclass
class ApprovalCondition: condition:str; priority:str="HIGH"
@dataclass
class GreenlightDecision:
    decision:str; score:int; confidence:float; blockers:list[str]=field(default_factory=list); warnings:list[str]=field(default_factory=list); approval_conditions:list[ApprovalCondition]=field(default_factory=list); evidence_gaps:list[str]=field(default_factory=list); recommended_action:str=""
    def to_dict(self): return {"decision":self.decision,"score":self.score,"confidence":self.confidence,"blockers":self.blockers,"warnings":self.warnings,"approval_conditions":[asdict(x) for x in self.approval_conditions],"evidence_gaps":self.evidence_gaps,"recommended_action":self.recommended_action}

def decide_greenlight(risk:dict[str,Any],schedule:dict[str,Any],limitations:list[str]|None=None)->GreenlightDecision:
    limitations=limitations or []; blockers=[]; warnings=[]; conditions=[]
    for r in risk.get("risks",[]):
        if r.get("severity")=="CRITICAL": blockers.append(r.get("title","Critical risk"))
        elif r.get("severity") in {"HIGH","MEDIUM"}: warnings.append(r.get("title","Material risk"))
    if schedule.get("status")=="CONFLICT": blockers.append("Schedule conflict")
    elif schedule.get("status")=="INSUFFICIENT_EVIDENCE": warnings.append("Schedule evidence gap")
    if limitations: warnings.extend(limitations)
    if blockers: decision="BLOCKED"; score=20; action="Resolve blocking production constraints before shooting."
    elif warnings: decision="WARNING"; score=68; action="Proceed only after the listed verification conditions are satisfied."
    else: decision="GREENLIGHT"; score=92; action="Production can proceed against the supplied evidence and schedule."
    if warnings: conditions.append(ApprovalCondition("Verify outstanding access, permit, schedule, and evidence conditions."))
    confidence=0.95 if not limitations else 0.88
    return GreenlightDecision(decision,score,confidence,blockers,warnings,conditions,limitations,action)

def greenlight_engine_tool(objective:str,risk_assessment:dict[str,Any],schedule_plan:dict[str,Any],intelligence_limitations:list[str]|None=None)->dict[str,Any]: return decide_greenlight(risk_assessment,schedule_plan,intelligence_limitations).to_dict()
