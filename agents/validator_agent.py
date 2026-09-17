import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from models.schemas import ValidationResult, ValidationIssue
from utils.retry import retry

load_dotenv()


@retry(max_attempts=3, delay=2, backoff=2)
def validate_claims(
    claims: list,
    sources: list,
    groq_api_key: str | None = None
) -> ValidationResult:

    # ==================================================
    # API KEY
    # ==================================================

    api_key = groq_api_key or os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "Groq API key is missing."
        )

    # ==================================================
    # LIMIT INPUT SIZE
    # ==================================================
    # Groq currently allows around 8,000 TPM for your
    # service tier. We therefore keep the validation
    # prompt relatively small.

    claims_to_validate = claims[:8]

    print(
        f"\n🔍 Validating "
        f"{len(claims_to_validate)} claims..."
    )

    # ==================================================
    # CREATE SOURCE MAP
    # ==================================================

    source_map = {
        source.id: source
        for source in sources
    }

    # ==================================================
    # LOCAL VALIDATION
    # ==================================================
    # Check source IDs before sending anything to Groq.

    invalid_claims = []
    local_issues = []

    for claim in claims_to_validate:

        # Claim has no evidence
        if not claim.evidence:

            invalid_claims.append(
                claim.claim
            )

            local_issues.append(
                ValidationIssue(
                    claim=claim.claim,
                    reason=(
                        "Claim has no supporting "
                        "evidence."
                    ),
                    severity="high"
                )
            )

            continue

        # Check every evidence source ID
        for evidence in claim.evidence:

            if evidence.source_id not in source_map:

                invalid_claims.append(
                    claim.claim
                )

                local_issues.append(
                    ValidationIssue(
                        claim=claim.claim,
                        reason=(
                            f"Invalid source ID: "
                            f"{evidence.source_id}"
                        ),
                        severity="high"
                    )
                )

    # Remove duplicate invalid claims
    invalid_claims = list(
        dict.fromkeys(invalid_claims)
    )

    # ==================================================
    # BUILD COMPACT VALIDATION CONTEXT
    # ==================================================

    claims_text = ""

    for i, claim in enumerate(
        claims_to_validate,
        start=1
    ):

        claims_text += f"""

CLAIM {i}:
{claim.claim}

EVIDENCE:
"""

        if not claim.evidence:

            claims_text += (
                "No evidence provided.\n"
            )

            continue

        # Limit evidence items per claim
        for evidence in claim.evidence[:3]:

            source = source_map.get(
                evidence.source_id
            )

            if not source:
                continue

            # Keep source content very small
            source_excerpt = (
                source.content[:400]
                if source.content
                else ""
            )

            claims_text += f"""

SOURCE ID:
{source.id}

SOURCE TITLE:
{source.title}

SOURCE DOMAIN:
{source.domain}

SOURCE QUALITY:
{source.quality_score:.2f}

SOURCE EXCERPT:
{source_excerpt}

CLAIM EVIDENCE:
{evidence.evidence[:500]}

--------------------------------
"""

    # ==================================================
    # LLM
    # ==================================================

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

    # ==================================================
    # VALIDATION PROMPT
    # ==================================================

    prompt = f"""
You are an expert research fact-checking agent.

Your task is to validate the supplied claims
against their supplied evidence.

Do NOT use outside knowledge.

CLAIMS AND EVIDENCE:

{claims_text}

For every claim:

1. Check whether the supplied evidence
   reasonably supports the claim.

2. Identify unsupported or weak claims.

3. Identify contradictions if the supplied
   sources disagree.

4. Consider source quality.

5. Do not invent facts.

6. Do not invent sources.

7. Do not assume information that is not
   present in the supplied evidence.

8. A claim without adequate evidence should
   be considered unsupported.

Return ONLY valid JSON.

Required format:

{{
    "valid": true,
    "invalid_claims": [],
    "issues": [],
    "conflicts": [],
    "score": 0.85
}}

For issues use:

{{
    "claim": "The claim being evaluated",
    "reason": "Why the evidence is weak or insufficient",
    "severity": "medium"
}}

Severity must be one of:

"low"
"medium"
"high"

Scoring:

1.0 = Excellent evidence
0.8 = Strong evidence
0.6 = Reasonable evidence with limitations
0.4 = Weak evidence
0.2 = Very weak evidence
0.0 = Unsupported

IMPORTANT:

You MUST return all five fields:

- valid
- invalid_claims
- issues
- conflicts
- score

Do not omit any field.

"invalid_claims" must be a list.

"issues" must be a list.

"conflicts" must be a list.

"score" must be a number between 0 and 1.

Return JSON only.
"""

    # ==================================================
    # CALL GROQ
    # ==================================================

    response = llm.invoke(prompt)

    # ==================================================
    # PARSE JSON
    # ==================================================

    try:

        data = json.loads(
            response.content
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            "Validator returned invalid JSON."
        ) from e

    # ==================================================
    # SAFE DEFAULTS
    # ==================================================

    data.setdefault(
        "valid",
        False
    )

    data.setdefault(
        "invalid_claims",
        []
    )

    data.setdefault(
        "issues",
        []
    )

    data.setdefault(
        "conflicts",
        []
    )

    data.setdefault(
        "score",
        0.0
    )

    # ==================================================
    # NORMALIZE TYPES
    # ==================================================

    if not isinstance(
        data["valid"],
        bool
    ):
        data["valid"] = False

    if not isinstance(
        data["invalid_claims"],
        list
    ):
        data["invalid_claims"] = []

    if not isinstance(
        data["issues"],
        list
    ):
        data["issues"] = []

    if not isinstance(
        data["conflicts"],
        list
    ):
        data["conflicts"] = []

    # ==================================================
    # NORMALIZE SCORE
    # ==================================================

    try:

        data["score"] = float(
            data["score"]
        )

    except (
        TypeError,
        ValueError
    ):

        data["score"] = 0.0

    data["score"] = max(
        0.0,
        min(
            1.0,
            data["score"]
        )
    )

    # ==================================================
    # PYDANTIC VALIDATION
    # ==================================================

    try:

        result = ValidationResult(
            **data
        )

    except Exception as e:

        print(
            "\n⚠️ Validator response "
            "could not be parsed."
        )

        print(
            f"Validator error: {e}"
        )

        result = ValidationResult(
            valid=False,
            invalid_claims=[],
            issues=[],
            conflicts=[],
            score=0.0
        )

    # ==================================================
    # COMBINE LOCAL + LLM RESULTS
    # ==================================================

    all_invalid_claims = list(
        dict.fromkeys(
            invalid_claims
            + result.invalid_claims
        )
    )

    all_issues = (
        local_issues
        + result.issues
    )

    # ==================================================
    # FINAL VALIDATION STATUS
    # ==================================================

    final_valid = (
        result.valid
        and len(all_invalid_claims) == 0
    )

    final_score = max(
        0.0,
        min(
            1.0,
            result.score
        )
    )

    # ==================================================
    # PRINT RESULTS
    # ==================================================

    print(
        f"\nValidation: {final_valid}"
    )

    print(
        f"Validation score: "
        f"{final_score:.2f}"
    )

    if all_invalid_claims:

        print(
            "\n⚠️ Invalid claims:"
        )

        for claim in all_invalid_claims:

            print(
                f"- {claim}"
            )

    if result.conflicts:

        print(
            "\n⚔️ Source conflicts:"
        )

        for conflict in result.conflicts:

            print(
                f"- {conflict}"
            )

    # ==================================================
    # RETURN FINAL RESULT
    # ==================================================

    return ValidationResult(
        valid=final_valid,
        invalid_claims=all_invalid_claims,
        issues=all_issues,
        conflicts=result.conflicts,
        score=final_score
    )