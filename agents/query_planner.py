import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from utils.retry import retry


load_dotenv()


@retry(
    max_attempts=3,
    delay=2,
    backoff=2
)
def generate_research_queries(
    topic: str,
    num_queries: int = 6,
    groq_api_key: str | None = None
) -> list[str]:

    """
    Generate intelligent research queries
    for a given topic.

    Parameters
    ----------
    topic:
        Research topic.

    num_queries:
        Number of queries to generate.

    groq_api_key:
        User-provided Groq API key.
        Falls back to GROQ_API_KEY from .env.
    """

    # ========================================
    # GET API KEY
    # ========================================

    api_key = (
        groq_api_key
        or os.getenv("GROQ_API_KEY")
    )

    if not api_key:

        raise ValueError(
            "Groq API key is missing. "
            "Please provide a Groq API key."
        )

    # ========================================
    # CREATE LLM
    # ========================================

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

    # ========================================
    # PROMPT
    # ========================================

    prompt = f"""
You are an expert research strategist.

Your task is to create a research plan for:

TOPIC:
{topic}

Generate exactly {num_queries}
high-quality search queries.

The queries should investigate
different dimensions of the topic.

Consider:

1. Current state
2. Statistics and quantitative data
3. Recent developments
4. Major challenges
5. Opportunities
6. Future outlook

Make the queries:

- Specific
- Search-friendly
- Non-duplicative
- Useful for serious research
- Focused on factual information

Avoid vague queries.

Do not answer the topic.
Only generate search queries.

Return ONLY valid JSON.

Required format:

{{
    "queries": [
        "query 1",
        "query 2",
        "query 3",
        "query 4",
        "query 5",
        "query 6"
    ]
}}

Rules:

- Return exactly {num_queries} queries.
- Every query must be a string.
- Do not include explanations.
- Do not include Markdown.
- Do not include duplicate queries.
- Return JSON only.
"""

    # ========================================
    # CALL GROQ
    # ========================================

    response = llm.invoke(
        prompt
    )

    # ========================================
    # PARSE JSON
    # ========================================

    data = json.loads(
        response.content
    )

    queries = data.get(
        "queries",
        []
    )

    # ========================================
    # CLEAN QUERIES
    # ========================================

    cleaned_queries = []

    for query in queries:

        if not isinstance(
            query,
            str
        ):
            continue

        query = query.strip()

        if not query:
            continue

        if query in cleaned_queries:
            continue

        cleaned_queries.append(
            query
        )

    # ========================================
    # FALLBACK
    # ========================================

    if not cleaned_queries:

        raise ValueError(
            "Query planner returned "
            "no valid research queries."
        )

    # ========================================
    # RETURN
    # ========================================

    return cleaned_queries[:num_queries]