from pydantic import BaseModel, Field


class Source(BaseModel):
    id: str
    title: str
    url: str
    content: str
    domain: str
    quality_score: float = 0.5


class Evidence(BaseModel):
    source_id: str
    evidence: str


class Claim(BaseModel):
    claim: str
    evidence: list[Evidence]


class AnalysisResult(BaseModel):
    analysis: str = ""
    claims: list[Claim] = []
    needs_more_research: bool = False
    missing_information: list[str] = []
    confidence_score: float = 0.75
class ValidationIssue(BaseModel):
    claim: str
    reason: str
    severity: str = "medium"


class ValidationResult(BaseModel):
    valid: bool
    invalid_claims: list[str]
    issues: list[ValidationIssue]
    conflicts: list[str]
    score: float