"""Pydantic schemas exposed by the algorithm catalog API."""

from pydantic import BaseModel, ConfigDict, Field


class AlgorithmSummary(BaseModel):
    """Compact algorithm representation for the catalog page."""

    slug: str
    title: str
    category: str
    short_description: str
    difficulty: str


class AlgorithmDetail(AlgorithmSummary):
    """Full educational and formal description of an algorithm."""

    description: str
    input_data: str
    output_data: str
    preconditions: str
    postconditions: str
    invariant_description: str | None = None
    pseudocode: str
    default_proof: str = Field(
        description="Initial Lean proof block offered in the workspace."
    )


class ProofVerificationRequest(BaseModel):
    """Proof text that will be embedded into an approved Lean template."""

    proof_code: str = Field(min_length=1, max_length=20_000)


class ProofVerificationResponse(BaseModel):
    """Normalized result of one proof-engine invocation."""

    status: str
    duration_ms: int
    diagnostic: str
    engine_available: bool
    model_config = ConfigDict(extra="forbid")
