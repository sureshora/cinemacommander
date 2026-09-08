from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

CATEGORIES=("location_access","permits","operating_hours","transport_logistics","weather_environment","production_dependency")
TERMS={
"location_access":("access","entry","entrance","closure","location","site","venue","waterfront","parking","filming"),
"permits":("permit","permission","license","licence","authorization","authorisation","approval"),
"operating_hours":("hours","opening","open","closing","closed","24-hour","night","overnight","curfew"),
"transport_logistics":("transport","traffic","road","parking","vehicle","transit","bus","train","logistics","delivery","loading"),
"weather_environment":("weather","rain","storm","wind","temperature","humidity","flood","environment","sunset"),
"production_dependency":("crew","equipment","security","safety","crowd","noise","power","electricity","insurance","restriction"),}

@dataclass
class ProductionFinding:
    category:str; statement:str; relevance:str="MEDIUM"; confidence:float=0.55; evidence_urls:list[str]=field(default_factory=list); evidence_titles:list[str]=field(default_factory=list)
@dataclass
class ProductionIntelligenceReport:
    objective:str; finding_count:int; evidence_count:int; coverage:dict[str,int]; findings:list[ProductionFinding]; evidence:list[dict[str,Any]]; limitations:list[str]=field(default_factory=list)
    def to_dict(self): return {"objective":self.objective,"finding_count":self.finding_count,"evidence_count":self.evidence_count,"coverage":self.coverage,"findings":[asdict(x) for x in self.findings],"evidence":self.evidence,"limitations":self.limitations}

def build_production_intelligence(objective:str,evidence:list[dict[str,Any]],max_findings:int=12)->ProductionIntelligenceReport:
    items=[dict(x) for x in evidence if x.get("url")]; coverage={x:0 for x in CATEGORIES}; findings=[]
    for item in items:
        text=" ".join(str(item.get(k) or "") for k in ("title","excerpt","snippet")).lower()
        cats=[c for c,terms in TERMS.items() if any(t in text for t in terms)] or ["production_dependency"]
        for cat in cats:
            if len(findings)>=max_findings: break
            coverage[cat]+=1; statement=item.get("excerpt") or item.get("snippet") or item.get("title") or item["url"]
            findings.append(ProductionFinding(cat,str(statement).strip(),"HIGH" if cat in {"permits","operating_hours"} else "MEDIUM",0.72 if item.get("excerpt") else 0.58,[str(item["url"])],[str(item.get("title") or item["url"])]) )
    limitations=[]
    if not items: limitations.append("No usable Parallel evidence was returned.")
    uncovered=[c for c,n in coverage.items() if n==0]
    if uncovered: limitations.append("No evidence coverage for: "+", ".join(uncovered)+".")
    return ProductionIntelligenceReport(objective,len(findings),len(items),coverage,findings,items,limitations)

def production_intelligence_tool(objective:str,evidence:list[dict[str,Any]])->dict[str,Any]: return build_production_intelligence(objective,evidence).to_dict()
