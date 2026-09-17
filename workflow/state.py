from typing import TypedDict

from models.schemas import Source, Claim


class ResearchState(TypedDict):
    # User input
    topic: str

    # Query Planner output
    research_queries: list[str]

    # Research data
    sources: list[Source]

    # Analyst output
    analysis: str
    claims: list[Claim]
    needs_more_research: bool
    missing_information: list[str]
    confidence_score: float

    # Validator output
    validation_score: float
    validation_issues: list[str]

    # Writer output
    report: str

    # Workflow control
    research_round: int
    max_research_rounds: int

    # Runtime API keys
    groq_api_key: str
    tavily_api_key: str