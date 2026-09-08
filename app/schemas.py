from datetime import datetime
from pydantic import BaseModel,Field
class ActivityInput(BaseModel): name:str; duration_minutes:int=Field(gt=0)
class ConstraintInput(BaseModel): name:str; constraint_type:str; description:str; hard:bool=True; earliest:datetime|None=None; latest:datetime|None=None; source_urls:list[str]=Field(default_factory=list)
class ScheduleRequest(BaseModel): shoot_start:datetime; shoot_end:datetime; activities:list[ActivityInput]; constraints:list[ConstraintInput]=Field(default_factory=list); buffer_minutes:int=Field(default=30,ge=0,le=240)
class ScheduleResponse(BaseModel): status:str; blocks:list[dict]; conflicts:list[dict]; buffer_minutes:int; utilization_percent:float; assumptions:list[str]; recommendations:list[str]
