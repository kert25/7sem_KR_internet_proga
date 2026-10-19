"""FastAPI entry point for the algorithm correctness proving system."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.schemas.algorithm import (
    AlgorithmDetail,
    AlgorithmSummary,
    ProofVerificationRequest,
    ProofVerificationResponse,
)
from app.services.algorithm_catalog import get_algorithm, list_algorithms
from app.services.proof_runner import ProofRunner
from app.services.proof_templates import get_proof_template


app = FastAPI(
    title="Algorithm Correctness Prover API",
    version="0.1.0",
    description=(
        "API веб-системы автоматизированной проверки корректности алгоритмов "
        "на основе интерактивного theorem proving."
    ),
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Provide a lightweight endpoint for local and container health checks."""

    return {"status": "ok"}


@app.get(
    f"{settings.api_prefix}/algorithms",
    response_model=list[AlgorithmSummary],
    tags=["algorithms"],
)
def read_algorithms() -> list[AlgorithmSummary]:
    """Return published algorithm cards from the initial catalog."""

    return list(list_algorithms())


@app.get(
    f"{settings.api_prefix}/algorithms/{{slug}}",
    response_model=AlgorithmDetail,
    tags=["algorithms"],
)
def read_algorithm(slug: str) -> AlgorithmDetail:
    """Return the full educational specification for one algorithm."""

    algorithm = get_algorithm(slug)
    if algorithm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Алгоритм не найден.",
        )
    return algorithm


@app.post(
    f"{settings.api_prefix}/algorithms/{{slug}}/verify",
    response_model=ProofVerificationResponse,
    tags=["proofs"],
)
def verify_proof(slug: str, payload: ProofVerificationRequest) -> ProofVerificationResponse:
    """Verify a proof block against the approved Lean template for an algorithm."""

    if get_algorithm(slug) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Алгоритм не найден.",
        )

    template = get_proof_template(slug)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Для этого алгоритма формальная модель ещё не добавлена.",
        )

    try:
        result = ProofRunner(get_settings()).verify(template, payload.proof_code)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return ProofVerificationResponse(
        status=result.status,
        duration_ms=result.duration_ms,
        diagnostic=result.diagnostic,
        engine_available=result.engine_available,
    )
