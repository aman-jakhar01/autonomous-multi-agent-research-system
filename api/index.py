import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from workflow.orchestrator import build_workflow


app = FastAPI(
    title="Autonomous Multi-Agent Research API",
    version="1.0.0",
)


class ResearchRequest(BaseModel):
    topic: str
    groq_api_key: str | None = None
    tavily_api_key: str | None = None
    max_research_rounds: int = 3


class ResearchResponse(BaseModel):
    topic: str
    report: str
    sources: int
    claims: int
    confidence_score: float
    validation_score: float
    research_rounds: int


@app.get("/")
def home():
    return {
        "name": "Autonomous Multi-Agent Research API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):

    groq_api_key = (
        request.groq_api_key
        or os.getenv("GROQ_API_KEY")
    )

    tavily_api_key = (
        request.tavily_api_key
        or os.getenv("TAVILY_API_KEY")
    )

    if not groq_api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key is missing.",
        )

    if not tavily_api_key:
        raise HTTPException(
            status_code=400,
            detail="Tavily API key is missing.",
        )

    if not request.topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Research topic cannot be empty.",
        )

    if not 1 <= request.max_research_rounds <= 5:
        raise HTTPException(
            status_code=400,
            detail="max_research_rounds must be between 1 and 5.",
        )

    try:

        workflow = build_workflow()

        initial_state = {
            "topic": request.topic.strip(),
            "research_queries": [],
            "sources": [],
            "analysis": "",
            "claims": [],
            "needs_more_research": False,
            "missing_information": [],
            "confidence_score": 0.0,
            "validation_score": 0.0,
            "validation_issues": [],
            "report": "",
            "research_round": 0,
            "max_research_rounds": request.max_research_rounds,
            "groq_api_key": groq_api_key,
            "tavily_api_key": tavily_api_key,
        }

        result = workflow.invoke(initial_state)

        return ResearchResponse(
            topic=request.topic.strip(),
            report=result.get("report", ""),
            sources=len(result.get("sources", [])),
            claims=len(result.get("claims", [])),
            confidence_score=result.get(
                "confidence_score",
                0.0,
            ),
            validation_score=result.get(
                "validation_score",
                0.0,
            ),
            research_rounds=result.get(
                "research_round",
                0,
            ),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Research workflow failed: {str(e)}",
        )