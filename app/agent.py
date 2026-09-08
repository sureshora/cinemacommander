"""Cinema Commander multi-agent architecture."""

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.genai import types
from vertexai.agent_engines import AdkApp

from .config import settings
from .intelligence import production_intelligence_tool
from .greenlight import greenlight_engine_tool
from .risk import risk_engine_tool
from .research_tools import parallel_web_search
from .scheduling_tools import evaluate_production_schedule

COMMON_OUTPUT_RULES = """
Return concise operational analysis. Do not invent live external facts.
Clearly label assumptions. Your output will be consumed by another agent.
"""


def llm_agent(name: str, description: str, instruction: str) -> Agent:
    return Agent(
        model=settings.gemini_model,
        name=name,
        description=description,
        instruction=COMMON_OUTPUT_RULES + "\n" + instruction,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.15,
            max_output_tokens=900,
        ),
    )


production_planner = llm_agent(
    "production_planner",
    "Converts a film brief into production constraints and dependencies.",
    """
You are the Production Planner.
Extract the shoot objective, dates/windows, location requirements,
cast/crew/equipment constraints, hard constraints, soft constraints,
and dependencies. Create a compact planning brief for downstream agents.
""",
)

research_scout = Agent(
    model=settings.gemini_model,
    name="research_scout",
    description="Researches live production constraints using Parallel Search.",
    instruction=COMMON_OUTPUT_RULES + """
You are the Research Scout.

Turn the production brief into evidence-backed research. First identify the
most important external questions, then call parallel_web_search.

Prioritize location/access, permits, operating hours, transport/logistics,
weather/environmental factors, and other production dependencies.

Return the evidence as a compact JSON-like list containing title, url and
excerpt. Do not make factual claims that are not supported by returned evidence.
If evidence is insufficient, say so explicitly.
""",
    tools=[parallel_web_search],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=1200,
    ),
)

production_intelligence = Agent(
    model=settings.gemini_model,
    name="production_intelligence",
    description="Transforms research evidence into structured cinema production intelligence.",
    instruction=COMMON_OUTPUT_RULES + """
You are the Production Intelligence Agent.

The preceding Research Scout output contains the latest research evidence.
Extract its evidence items and call production_intelligence_tool exactly once.
Pass the production objective and the evidence list to the tool.

Then summarize the returned report for downstream agents using these sections:
- COVERAGE
- KEY FINDINGS
- EVIDENCE
- LIMITATIONS

Never turn an unsupported assumption into a fact. Preserve source URLs for
all externally derived findings.
""",
    tools=[production_intelligence_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.05,
        max_output_tokens=1400,
    ),
)

risk_officer = Agent(
    model=settings.gemini_model,
    name="risk_officer",
    description="Scores and structures production risks from evidence-backed intelligence.",
    instruction=COMMON_OUTPUT_RULES + """
You are the Risk Officer.
The preceding Production Intelligence Agent output contains structured findings.
Extract the objective and findings, then call risk_engine_tool exactly once.
Use the returned risk register as the authoritative risk assessment.
Summarize: OVERALL RISK, TOP RISKS, MITIGATIONS, and LIMITATIONS.
Never invent external facts or source URLs. Keep every research-derived risk traceable.
""",
    tools=[risk_engine_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.05,
        max_output_tokens=1400,
    ),
)

schedule_agent = Agent(
    model=settings.gemini_model,
    name="schedule_agent",
    description="Builds a deterministic, constraint-aware production schedule assessment.",
    instruction=COMMON_OUTPUT_RULES + """
You are the Schedule Agent.
Extract the production window, activities, durations and evidenced constraints
from the preceding outputs, then call evaluate_production_schedule exactly once.
Use its returned schedule as authoritative for timing arithmetic and conflicts.
Return: STATUS, TIMELINE, CONFLICTS, UTILIZATION, and REPLANNING TRIGGERS.
""",
    tools=[evaluate_production_schedule],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.05,
        max_output_tokens=1400,
    ),
)

greenlight_director = Agent(
    model=settings.gemini_model,
    name="greenlight_director",
    description="Makes the final evidence-aware production decision.",
    instruction=COMMON_OUTPUT_RULES + """
You are the Greenlight Director.
Review the planning, production-intelligence, risk, and schedule outputs.
Extract the objective, structured risk assessment, schedule plan, and intelligence
limitations, then call greenlight_engine_tool exactly once.
Treat its status as authoritative: GREENLIGHT, WARNING, or BLOCKED.
Present the result as an executive production decision with: STATUS, SCORE,
CRITICAL BLOCKERS, WARNINGS, APPROVAL CONDITIONS, EVIDENCE GAPS, and NEXT ACTION.
Never convert an evidence gap into approval.
""",
    tools=[greenlight_engine_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.05,
        max_output_tokens=1600,
    ),
)

planning_and_research = ParallelAgent(
    name="planning_and_research_team",
    description="Runs production planning and live research concurrently.",
    sub_agents=[production_planner, research_scout],
)

risk_and_schedule = ParallelAgent(
    name="risk_and_schedule_team",
    description="Runs risk and schedule assessment after production intelligence is available.",
    sub_agents=[risk_officer, schedule_agent],
)

root_agent = SequentialAgent(
    name="cinema_commander_workflow",
    description="Deterministic production intelligence and greenlight workflow.",
    sub_agents=[
        planning_and_research,
        production_intelligence,
        risk_and_schedule,
        greenlight_director,
    ],
)

adk_app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
