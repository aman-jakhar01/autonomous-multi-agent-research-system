import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from utils.retry import retry

load_dotenv()


@retry(max_attempts=3, delay=2, backoff=2)
def write_report(
    topic: str,
    analysis: str,
    claims: list,
    sources: list,
    groq_api_key: str | None = None
) -> str:

    # ==================================================
    # API KEY
    # ==================================================

    api_key = groq_api_key or os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "Groq API key is missing."
        )

    # ==================================================
    # LIMIT CONTEXT
    # ==================================================

    # Only use the most important claims.
    claims_to_write = claims[:8]

    # Only include sources actually referenced
    # by the selected claims.
    used_source_ids = set()

    for claim in claims_to_write:

        for evidence in claim.evidence[:3]:

            used_source_ids.add(
                evidence.source_id
            )

    selected_sources = []

    for source in sources:

        if source.id in used_source_ids:

            selected_sources.append(source)

        if len(selected_sources) >= 12:
            break

    # ==================================================
    # SOURCE MAP
    # ==================================================

    source_map = {
        source.id: source
        for source in selected_sources
    }

    # ==================================================
    # BUILD CLAIM CONTEXT
    # ==================================================

    claims_text = ""

    for i, claim in enumerate(
        claims_to_write,
        start=1
    ):

        claims_text += f"""

CLAIM {i}:
{claim.claim}

"""

        if not claim.evidence:

            claims_text += (
                "Evidence: None\n"
            )

            continue

        for evidence in claim.evidence[:3]:

            source = source_map.get(
                evidence.source_id
            )

            if not source:
                continue

            claims_text += f"""

SOURCE ID:
{source.id}

SOURCE TITLE:
{source.title}

SOURCE URL:
{source.url}

SOURCE DOMAIN:
{source.domain}

SOURCE QUALITY:
{source.quality_score:.2f}

EVIDENCE:
{evidence.evidence[:500]}

SOURCE EXCERPT:
{source.content[:300]}

--------------------------------
"""

    # ==================================================
    # SOURCE LIST
    # ==================================================

    sources_text = ""

    for i, source in enumerate(
        selected_sources,
        start=1
    ):

        sources_text += (
            f"[{i}] "
            f"{source.title} — "
            f"{source.url}\n"
        )

    # ==================================================
    # LIMIT ANALYSIS
    # ==================================================

    analysis_text = analysis[:5000]

    # ==================================================
    # LLM
    # ==================================================

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        api_key=api_key
    )

    # ==================================================
    # WRITING PROMPT
    # ==================================================

    prompt = f"""
You are a professional research report writer.

Write a concise, high-quality research report
using ONLY the supplied research.

TOPIC:
{topic}

ANALYSIS:
{analysis_text}

VERIFIED CLAIMS AND EVIDENCE:
{claims_text}

SOURCES:
{sources_text}

IMPORTANT RULES:

1. Use ONLY the supplied information.

2. Do not invent facts.

3. Do not use outside knowledge.

4. Do not create fake citations.

5. Do not create fake URLs.

6. Every important factual statement must
   be supported by the supplied evidence.

7. Use numbered citations such as [1], [2],
   [3] where appropriate.

8. Do not mention source IDs in normal prose.

9. If evidence is insufficient, do not make
   the unsupported claim.

10. If sources disagree, mention the conflict.

11. Keep the report concise and factual.

Write in Markdown.

REQUIRED STRUCTURE:

# {topic}

## Executive Summary

Summarize the most important findings.

## Introduction

Briefly explain the research topic.

## Key Findings

Present the strongest evidence-backed findings.

## Current State

Describe the current situation.

## Statistics and Trends

Include important statistics and trends
when supported by the evidence.

## Challenges

Describe the major challenges.

## Opportunities

Describe important opportunities.

## Future Outlook

Discuss the future direction based only
on the supplied research.

## Conclusion

Summarize the main findings.

## Sources

List the supplied sources using:

[1] Source Title — URL
[2] Source Title — URL

Return ONLY the Markdown report.
"""

    # ==================================================
    # GENERATE REPORT
    # ==================================================

    response = llm.invoke(prompt)

    report = response.content.strip()

    if not report:

        raise ValueError(
            "Writer returned an empty report."
        )

    return report