from google.adk.agents import Agent, SequentialAgent
from google.genai import types
from vertexai.agent_engines import AdkApp
from .config import settings
from .intelligence import production_intelligence_tool
from .greenlight import greenlight_engine_tool
from .risk import risk_engine_tool
from .research_tools import parallel_web_search
from .scheduling_tools import evaluate_production_schedule

COMMON_OUTPUT_RULES = "Return concise operational analysis. Do not invent live external facts. Clearly label assumptions."

def llm_agent(name, description, instruction):
    return Agent(model=settings.gemini_model,name=name,description=description,instruction=COMMON_OUTPUT_RULES+"\n"+instruction,generate_content_config=types.GenerateContentConfig(temperature=0.15,max_output_tokens=900))

production_planner = llm_agent("production_planner","Converts a film brief into production constraints and dependencies.","Extract objective, dates/windows, location, cast/crew/equipment constraints, hard and soft constraints, and dependencies.")

research_scout = Agent(model=settings.gemini_model,name="research_scout",description="Researches live production constraints using Parallel Search.",instruction=COMMON_OUTPUT_RULES+"\nResearch the production brief using parallel_web_search. Prioritize location/access, permits, operating hours, transport/logistics, weather/environment, and dependencies. Return title, url and excerpt. Never invent unsupported facts.",tools=[parallel_web_search],generate_content_config=types.GenerateContentConfig(temperature=0.1,max_output_tokens=1200))

production_intelligence = Agent(model=settings.gemini_model,name="production_intelligence",description="Transforms research evidence into structured production intelligence.",instruction=COMMON_OUTPUT_RULES+"\nExtract the Research Scout evidence and call production_intelligence_tool exactly once. Summarize coverage, findings, evidence and limitations.",tools=[production_intelligence_tool],generate_content_config=types.GenerateContentConfig(temperature=0.05,max_output_tokens=1400))

risk_officer = Agent(model=settings.gemini_model,name="risk_officer",description="Scores production risks from evidence-backed intelligence.",instruction=COMMON_OUTPUT_RULES+"\nExtract findings and call risk_engine_tool exactly once. Summarize overall risk, top risks, mitigations and limitations.",tools=[risk_engine_tool],generate_content_config=types.GenerateContentConfig(temperature=0.05,max_output_tokens=1400))

schedule_agent = Agent(model=settings.gemini_model,name="schedule_agent",description="Builds a deterministic production schedule assessment.",instruction=COMMON_OUTPUT_RULES+"\nExtract the production window, activities, durations and constraints, then call evaluate_production_schedule exactly once. Return status, timeline, conflicts, utilization and replanning triggers.",tools=[evaluate_production_schedule],generate_content_config=types.GenerateContentConfig(temperature=0.05,max_output_tokens=1400))

greenlight_director = Agent(model=settings.gemini_model,name="greenlight_director",description="Makes the final evidence-aware production decision.",instruction=COMMON_OUTPUT_RULES+"\nReview all preceding outputs, then call greenlight_engine_tool exactly once. Treat its status as authoritative: GREENLIGHT, WARNING or BLOCKED. Return status, score, blockers, warnings, approval conditions, evidence gaps and next action.",tools=[greenlight_engine_tool],generate_content_config=types.GenerateContentConfig(temperature=0.05,max_output_tokens=1600))

# HACK-CINE-014: deterministic sequential execution avoids the failing asyncio TaskGroup path in the hosted demo while retaining six specialized Gemini agents and live Parallel Search.
root_agent = SequentialAgent(name="cinema_commander_workflow",description="Multi-agent production intelligence and greenlight workflow.",sub_agents=[production_planner,research_scout,production_intelligence,risk_officer,schedule_agent,greenlight_director])

adk_app = AdkApp(agent=root_agent)
