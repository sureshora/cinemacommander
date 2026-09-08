from __future__ import annotations
from dataclasses import asdict,dataclass,field
from datetime import datetime,timedelta
from enum import Enum

class ScheduleStatus(str,Enum): FEASIBLE="FEASIBLE"; CONFLICT="CONFLICT"; INSUFFICIENT_EVIDENCE="INSUFFICIENT_EVIDENCE"
class ConstraintType(str,Enum): ACCESS="ACCESS"; PERMIT="PERMIT"; OPERATING_HOURS="OPERATING_HOURS"; LOGISTICS="LOGISTICS"; OTHER="OTHER"
@dataclass
class ScheduleConstraint:
    name:str; constraint_type:ConstraintType; description:str=""; hard:bool=True; earliest:datetime|None=None; latest:datetime|None=None; source_urls:list[str]=field(default_factory=list)
@dataclass
class ScheduleBlock:
    name:str; start:datetime; end:datetime; duration_minutes:int; status:str="PLANNED"; notes:str=""
@dataclass
class ScheduleConflict:
    constraint:str; severity:str; message:str; affected_blocks:list[str]=field(default_factory=list); source_urls:list[str]=field(default_factory=list)
@dataclass
class SchedulePlan:
    status:ScheduleStatus; blocks:list[ScheduleBlock]; conflicts:list[ScheduleConflict]; buffer_minutes:int; utilization_percent:float; assumptions:list[str]; recommendations:list[str]

def build_schedule(shoot_start:datetime,shoot_end:datetime,activities:list[tuple[str,int]],constraints:list[ScheduleConstraint]|None=None,buffer_minutes:int=30)->SchedulePlan:
    constraints=constraints or []; window=int((shoot_end-shoot_start).total_seconds()/60)
    if window<=0:return SchedulePlan(ScheduleStatus.CONFLICT,[],[ScheduleConflict("shoot_window","CRITICAL","Shoot end must be later than shoot start.")],0,0,[],["Provide a valid production window."])
    cur=shoot_start; blocks=[]; conflicts=[]; assumptions=[]
    if not constraints: assumptions.append("No external production constraints were supplied.")
    for name,duration in activities:
        end=cur+timedelta(minutes=duration); blocks.append(ScheduleBlock(name,cur,end,duration)); cur=end+timedelta(minutes=buffer_minutes)
    planned_end=blocks[-1].end if blocks else shoot_start
    if planned_end>shoot_end: conflicts.append(ScheduleConflict("shoot_window","CRITICAL",f"Planned work exceeds the available shoot window by {int((planned_end-shoot_end).total_seconds()/60)} minutes.",[b.name for b in blocks]))
    for c in constraints:
        if c.hard and c.earliest and shoot_start<c.earliest: conflicts.append(ScheduleConflict(c.name,"HIGH",f"Production begins before the allowed earliest time ({c.earliest.isoformat()}).",source_urls=c.source_urls))
        if c.hard and c.latest and cur>c.latest: conflicts.append(ScheduleConflict(c.name,"HIGH",f"Planned production plus buffer ends after the allowed latest time ({c.latest.isoformat()}).",[b.name for b in blocks],c.source_urls))
        if c.hard and c.constraint_type in {ConstraintType.ACCESS,ConstraintType.PERMIT} and c.earliest is None and c.latest is None: conflicts.append(ScheduleConflict(c.name,"MEDIUM",f"Timing for '{c.name}' is not evidenced; schedule cannot fully validate it.",source_urls=c.source_urls))
    utilization=round(min(100,(sum(b.duration_minutes for b in blocks)/window)*100),1)
    if any(c.severity=="CRITICAL" for c in conflicts): status=ScheduleStatus.CONFLICT
    elif any(c.severity=="MEDIUM" for c in conflicts): status=ScheduleStatus.INSUFFICIENT_EVIDENCE
    elif conflicts: status=ScheduleStatus.CONFLICT
    else: status=ScheduleStatus.FEASIBLE
    rec=["Re-run scheduling after resolving the highest-severity conflict."] if status!=ScheduleStatus.FEASIBLE else ["Schedule is arithmetically feasible; retain the planned buffer."]
    return SchedulePlan(status,blocks,conflicts,buffer_minutes,utilization,assumptions,rec)
