from datetime import datetime
from app.schedule import ConstraintType,ScheduleConstraint,build_schedule

def evaluate_production_schedule(shoot_start:str,shoot_end:str,activities:list[dict],constraints:list[dict]|None=None,buffer_minutes:int=30)->dict:
    parsed=[]
    for x in constraints or []:
        parsed.append(ScheduleConstraint(x["name"],ConstraintType(x["constraint_type"]),x.get("description",""),x.get("hard",True),datetime.fromisoformat(x["earliest"]) if x.get("earliest") else None,datetime.fromisoformat(x["latest"]) if x.get("latest") else None,x.get("source_urls",[])))
    p=build_schedule(datetime.fromisoformat(shoot_start),datetime.fromisoformat(shoot_end),[(x["name"],int(x["duration_minutes"])) for x in activities],parsed,buffer_minutes)
    return {"status":p.status.value,"blocks":[{"name":b.name,"start":b.start.isoformat(),"end":b.end.isoformat(),"duration_minutes":b.duration_minutes,"status":b.status,"notes":b.notes} for b in p.blocks],"conflicts":[{"constraint":c.constraint,"severity":c.severity,"message":c.message,"affected_blocks":c.affected_blocks,"source_urls":c.source_urls} for c in p.conflicts],"buffer_minutes":p.buffer_minutes,"utilization_percent":p.utilization_percent,"assumptions":p.assumptions,"recommendations":p.recommendations}
