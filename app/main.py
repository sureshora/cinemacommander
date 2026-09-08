from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse,StreamingResponse
from pydantic import BaseModel,Field
from .execution import execute_production_brief
from .greenlight import greenlight_engine_tool
from .intelligence import build_production_intelligence
from .live_execution import manager
from .parallel_search import ParallelSearchService
from .risk import risk_engine_tool
from .schedule import ConstraintType,ScheduleConstraint,build_schedule
app=FastAPI(title="Cinema Commander",version="0.12.0",description="Live Gemini multi-agent production intelligence control tower")
@app.get("/health")
def health(): return {"status":"ok","project":"Cinema Commander","milestone":"HACK-CINE-012","ai_runtime":"Google ADK + Gemini","partner_runtime":"Parallel Search API","live_stream":"SSE"}
@app.get("/",response_class=HTMLResponse)
def home(): return (Path(__file__).parent/"templates"/"index.html").read_text(encoding="utf-8")
class ProductionBrief(BaseModel): brief:str=Field(min_length=10)
@app.post("/api/agent/analyze")
async def analyze_brief(payload:ProductionBrief):
    trace,events=await execute_production_brief(payload.brief); return {"milestone":"HACK-CINE-012","agent":"cinema_commander_workflow","execution":trace.snapshot(),"events":events}
@app.post("/api/agent/run")
async def start_live_run(payload:ProductionBrief):
    run=manager.create(payload.brief); await manager.start(run); return {"execution_id":run.execution_id,"status":run.status,"stream_url":f"/api/agent/stream/{run.execution_id}"}
@app.get("/api/agent/stream/{execution_id}")
async def stream_live_run(execution_id:str):
    run=manager.runs.get(execution_id)
    if not run:return {"error":"execution_not_found"}
    async def gen():
        while True:
            item=await run.queue.get()
            if item is None:break
            yield f"data: {json.dumps(item,separators=(',',':'))}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})
@app.get("/api/agent/run/{execution_id}")
async def live_run_status(execution_id:str):
    run=manager.runs.get(execution_id)
    if not run:return {"error":"execution_not_found"}
    return {"execution_id":run.execution_id,"status":run.status,"snapshot":run.snapshot,"error":run.error}
class SearchRequest(BaseModel): objective:str=Field(min_length=10); search_queries:list[str]=Field(min_length=1,max_length=3)
@app.post("/api/research/search")
def research_search(payload:SearchRequest):
    evidence=ParallelSearchService().search(payload.objective,payload.search_queries); return {"milestone":"HACK-CINE-005","provider":"Parallel Search API","result_count":len(evidence),"evidence":evidence}
@app.post("/api/research/intelligence")
def research_intelligence(payload:SearchRequest):
    evidence=ParallelSearchService().search(payload.objective,payload.search_queries); return {"milestone":"HACK-CINE-006","intelligence":build_production_intelligence(payload.objective,evidence).to_dict()}
class RiskRequest(BaseModel): objective:str=Field(min_length=10); findings:list[dict]=Field(min_length=1,max_length=12)
@app.post("/api/risk/assess")
def risk_assess(payload:RiskRequest): return {"milestone":"HACK-CINE-007","risk_assessment":risk_engine_tool(payload.objective,payload.findings)}
class ScheduleRequest(BaseModel): shoot_start:str; shoot_end:str; activities:list[dict]; constraints:list[dict]=[]; buffer_minutes:int=Field(default=30,ge=0,le=240)
@app.post("/api/schedule/evaluate")
def schedule_evaluate(payload:ScheduleRequest):
    cs=[ScheduleConstraint(x["name"],ConstraintType(x["constraint_type"]),x.get("description",""),x.get("hard",True),datetime.fromisoformat(x["earliest"]) if x.get("earliest") else None,datetime.fromisoformat(x["latest"]) if x.get("latest") else None,x.get("source_urls",[])) for x in payload.constraints]
    p=build_schedule(datetime.fromisoformat(payload.shoot_start),datetime.fromisoformat(payload.shoot_end),[(x["name"],int(x["duration_minutes"])) for x in payload.activities],cs,payload.buffer_minutes)
    return {"milestone":"HACK-CINE-008","schedule":{"status":p.status.value,"blocks":[b.__dict__ for b in p.blocks],"conflicts":[c.__dict__ for c in p.conflicts],"buffer_minutes":p.buffer_minutes,"utilization_percent":p.utilization_percent,"assumptions":p.assumptions,"recommendations":p.recommendations}}
class GreenlightRequest(BaseModel): objective:str=Field(min_length=10); risk_assessment:dict; schedule_plan:dict; intelligence_report:dict={}
@app.post("/api/greenlight/decide")
def greenlight_decide(payload:GreenlightRequest): return {"milestone":"HACK-CINE-009","decision":greenlight_engine_tool(payload.objective,payload.risk_assessment,payload.schedule_plan,payload.intelligence_report.get("limitations",[]))}
