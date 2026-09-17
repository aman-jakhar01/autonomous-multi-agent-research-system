import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from models.schemas import AnalysisResult
from utils.retry import retry


load_dotenv()


# ============================================================
# ANALYST AGENT
# ============================================================

@retry(
    max_attempts=3,
    delay=2,
    backoff=2
)
def analyze_research(
    topic: str,
    sources: list,
    groq_api_key: str | None = None
) -> AnalysisResult:

    """
    Analyze collected research sources.

    The Groq API key can be supplied dynamically
    by the Streamlit user.

    Falls back to GROQ_API_KEY from .env.
    """

    # ========================================================
    # GET API KEY
    # ========================================================

    api_key = (
        groq_api_key
        or os.getenv("GROQ_API_KEY")
    )

    if not api_key:

        raise ValueError(
            "Groq API key is missing."
        )

    # ========================================================
    # CREATE LLM
    # ========================================================

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
        model_kwargs={
            "response_format": {
                "type": "json_object"
            }
        }
    )

    # ========================================================
    # PREPARE SOURCES
    # ========================================================

    research_text = ""

    # Limit context to prevent huge prompts
    selected_sources = sources[:12]

    for i, source in enumerate(
        selected_sources,
        start=1
    ):

        research_text += f"""
SOURCE ID:
{source.id}

TITLE:
{source.title}

URL:
{source.url}

DOMAIN:
{source.domain}

QUALITY SCORE:
{source.quality_score}

CONTENT:
{source.content[:1000]}

--------------------------------
"""

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are a professional research analyst.

TOPIC:
{topic}

SOURCES:
{research_text}

Analyze the supplied sources carefully.

Your responsibilities:

1. Identify important factual findings.
2. Extract claims that are supported by evidence.
3. Connect each claim to the correct source.
4. Identify missing information.
5. Identify contradictions when possible.
6. Do not invent facts.
7. Do not use outside knowledge.
8. Every factual claim must have evidence.
9. Every evidence item MUST use an EXACT
   source_id from the supplied sources.
10. Never invent source IDs.

Return ONLY valid JSON.

Required format:

{{
    "analysis": "Overall analysis of the research",

    "claims": [
        {{
            "claim": "A factual claim supported by the sources",

            "evidence": [
                {{
                    "source_id": "EXACT_SOURCE_ID",
                    "evidence": "Short supporting evidence"
                }}
            ]
        }}
    ],

    "needs_more_research": true,

    "missing_information": [
        "Specific information that is still missing"
    ],

    "confidence_score": 0.75
}}

Rules:

- confidence_score must be between 0 and 1.
- Do not invent statistics.
- Do not invent sources.
- Do not invent source IDs.
- Use only supplied sources.
- Keep evidence concise.
- Claims must be supported by evidence.
- If evidence is weak, mention it.
- If important information is missing,
  add it to missing_information.
- Return JSON only.
"""

    # ========================================================
    # CALL GROQ
    # ========================================================

    response = llm.invoke(
        prompt
    )

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        data = json.loads(
            response.content
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            "Analyst returned invalid JSON."
        ) from e

    # ========================================================
    # VALIDATE RESULT
    # ========================================================

    # Safely handle incomplete LLM JSON
    data.setdefault("analysis", "")
    data.setdefault("claims", [])
    data.setdefault("needs_more_research", False)
    data.setdefault("missing_information", [])
    data.setdefault("confidence_score", 0.75)

# Make sure values have the expected types
    if not isinstance(data["claims"], list):
        data["claims"] = []
    if not isinstance(data["missing_information"], list):
        data["missing_information"] = []

    if not isinstance(data["needs_more_research"], bool):
        data["needs_more_research"] = False

    if not isinstance(data["needs_more_research"], bool):
        data["needs_more_research"] = False

    try:
        data["confidence_score"] = float(data["confidence_score"])
    except (TypeError, ValueError):
        data["confidence_score"] = 0.75

    data["confidence_score"] = max(
        0.0,
        min(1.0, data["confidence_score"])
)

    result = AnalysisResult(**data)

    return result