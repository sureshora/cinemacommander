from dataclasses import dataclass,field
from datetime import datetime,timezone
from typing import Any
@dataclass
class AgentStep:
    name:str; status:str="PENDING"; started_at:str|None=None; completed_at:str|None=None; output:Any=None; error:str|None=None
    def start(self): self.status="RUNNING"; self.started_at=datetime.now(timezone.utc).isoformat()
    def complete(self,output:Any): self.status="COMPLETED"; self.output=output; self.completed_at=datetime.now(timezone.utc).isoformat()
    def fail(self,error:str): self.status="FAILED"; self.error=error; self.completed_at=datetime.now(timezone.utc).isoformat()
@dataclass
class ExecutionTrace:
    execution_id:str; status:str="PENDING"; steps:list[AgentStep]=field(default_factory=list)
    def begin(self): self.status="RUNNING"
    def finish(self): self.status="COMPLETED"
    def fail(self): self.status="FAILED"
    def snapshot(self): return {"execution_id":self.execution_id,"status":self.status,"steps":[{"name":s.name,"status":s.status,"started_at":s.started_at,"completed_at":s.completed_at,"output":s.output,"error":s.error} for s in self.steps]}
def create_trace(execution_id:str): return ExecutionTrace(execution_id,steps=[AgentStep(x) for x in ["production_planner","research_scout","production_intelligence","risk_officer","schedule_agent","greenlight_director"]])
