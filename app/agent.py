from google.adk.agents import Agent, SequentialAgent
from google.genai import types
from vertexai.agent_engines import AdkApp
from .config import settings

COMMON_OUTPUT_RULES = "Return concise operational analysis. Do not invent live external facts. Clearly label assumptions."


def llm_agent(name, description, instruction, max_output_tokens=900):
    return Agent(
        model=settings.gemini_model,
        name=name,
        description=description,
        instruction=COMMON_OUTPUT_RULES + "\n" + instruction,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=max_output_tokens,
        ),
    )


production_planner = llm_agent(
    "production_planner",
    "Converts a film brief into production constraints and dependencies.",
    "Extract objective, dates/windows, location, cast/crew/equipment constraints, hard and soft constraints, and dependencies.",
)

research_scout = llm_agent(
    "research_scout",
    "Analyzes live production evidence supplied by the runtime research service.",
    "Review the Parallel Search evidence included in the request. Summarize relevant location/access, permits, operating hours, transport/logistics, weather/environment, and production dependencies. Preserve source titles and URLs and never invent unsupported facts.",
    1200,
)

production_intelligence = llm_agent(
    "production_intelligence",
    "Transforms research evidence into structured production intelligence.",
    "Convert the supplied research into concise findings. Classify findings as location_access, permits, operating_hours, transport_logistics, weather_environment, or production_dependency. Identify evidence gaps and assumptions.",
    1200,
)

risk_officer = llm_agent(
    "risk_officer",
    "Scores and explains production risks from evidence-backed intelligence.",
    "Review the production intelligence and identify the most important operational risks, their likely consequences, mitigations, confidence, and evidence supporting each risk. Do not invent facts.",
    1200,
)

schedule_agent = llm_agent(
    "schedule_agent",
    "Assesses shooting-window feasibility and scheduling constraints.",
    "Evaluate the stated shooting window, activities, resources, buffers, and constraints. Identify conflicts, missing evidence, and practical replanning triggers. Do not invent exact operating hours when evidence is absent.",
    1200,
)

greenlight_director = llm_agent(
    "greenlight_director",
    "Makes the final evidence-aware production decision.",
    "Review all preceding workflow outputs and make a conservative final decision: GREENLIGHT, WARNING, or BLOCKED. Return the status, rationale, blockers, warnings, approval conditions, evidence gaps, and next action. Treat missing critical evidence as WARNING rather than inventing certainty.",
    1400,
)

# HACK-CINE-015: ADK function-calling was hanging in the hosted environment immediately after
# AsyncModels.generate_content. Runtime services are therefore executed by the application and
# their results are supplied to these six specialized Gemini agents as workflow context.
root_agent = SequentialAgent(
    name="cinema_commander_workflow",
    description="Multi-agent production intelligence and greenlight workflow.",
    sub_agents=[
        production_planner,
        research_scout,
        production_intelligence,
        risk_officer,
        schedule_agent,
        greenlight_director,
    ],
)

adk_app = AdkApp(agent=root_agent)
