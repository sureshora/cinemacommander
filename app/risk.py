from __future__ import annotations
from dataclasses import asdict,dataclass,field
from typing import Any
BASE={"location_access":55,"permits":70,"operating_hours":65,"transport_logistics":50,"weather_environment":55,"production_dependency":45}
HIGH=("closed","closure","curfew","prohibited","not permitted","permit required","restricted","storm","flood","unsafe","danger","emergency","no access","unavailable")
MED=("may require","requires","limited","traffic","parking","night","overnight","weather","rain","wind","noise","crowd")
@dataclass
class ProductionRisk:
    risk_id:str; category:str; severity:str; score:int; title:str; trigger:str; consequence:str; mitigation:str; confidence:float; evidence_urls:list[str]=field(default_factory=list); evidence_titles:list[str]=field(default_factory=list)
@dataclass
class RiskAssessment:
    objective:str; risk_count:int; overall_severity:str; overall_score:int; risks:list[ProductionRisk]; blockers:list[str]; limitations:list[str]
    def to_dict(self): return {"objective":self.objective,"risk_count":self.risk_count,"overall_severity":self.overall_severity,"overall_score":self.overall_score,"risks":[asdict(x) for x in self.risks],"blockers":self.blockers,"limitations":self.limitations}

def assess_risks(objective:str,findings:list[dict[str,Any]])->RiskAssessment:
    risks=[]
    for i,f in enumerate(findings):
        text=str(f.get("statement","")).lower(); score=BASE.get(f.get("category"),45)
        if any(x in text for x in HIGH): score+=25
        elif any(x in text for x in MED): score+=10
        score=min(100,score); sev="CRITICAL" if score>=85 else "HIGH" if score>=70 else "MEDIUM" if score>=50 else "LOW"
        risks.append(ProductionRisk(f"RISK-{i+1:03}",f.get("category","production_dependency"),sev,score,f"{f.get('category','Production')} constraint",str(f.get("statement","")),"May disrupt production access, safety, timing, or logistics.","Verify the constraint and re-run the production decision before shooting.",float(f.get("confidence",0.5)),f.get("evidence_urls",[]),f.get("evidence_titles",[])))
    risks.sort(key=lambda x:x.score,reverse=True); overall=risks[0].score if risks else 0; severity=risks[0].severity if risks else "INSUFFICIENT_EVIDENCE"
    blockers=[r.title for r in risks if r.severity=="CRITICAL"]
    return RiskAssessment(objective,len(risks),severity,overall,risks,blockers,[] if risks else ["No production findings were supplied."])

def risk_engine_tool(objective:str,findings:list[dict[str,Any]])->dict[str,Any]: return assess_risks(objective,findings).to_dict()
