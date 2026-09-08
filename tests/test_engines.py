from datetime import datetime
from app.intelligence import build_production_intelligence
from app.risk import risk_engine_tool
from app.schedule import build_schedule,ScheduleStatus
from app.greenlight import greenlight_engine_tool

def test_intelligence_is_evidence_linked():
    report=build_production_intelligence('night shoot',[{'title':'Permit Notice','url':'https://example.com/p','excerpt':'Permit required for filming.'}])
    assert report.findings[0].evidence_urls==['https://example.com/p']

def test_schedule_detects_overflow():
    p=build_schedule(datetime(2026,9,9,22),datetime(2026,9,10,0),[('Scene',150)],[],30)
    assert p.status==ScheduleStatus.CONFLICT

def test_greenlight_blocks_critical_risk():
    risk=risk_engine_tool('shoot',[{'category':'permits','statement':'Permit required and access restricted.','confidence':.9,'evidence_urls':['https://example.com/p']}])
    decision=greenlight_engine_tool('shoot',risk,{'status':'FEASIBLE'},[])
    assert decision['decision'] in {'WARNING','BLOCKED'}
