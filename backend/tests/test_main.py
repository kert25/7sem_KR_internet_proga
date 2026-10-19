from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings
from app.services.proof_runner import ProofRunner


client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_catalog_contains_initial_algorithms() -> None:
    response = client.get("/api/v1/algorithms")

    assert response.status_code == 200
    assert {algorithm["slug"] for algorithm in response.json()} == {
        "linear-search",
        "maximum-in-list",
    }


def test_algorithm_detail_returns_specification() -> None:
    response = client.get("/api/v1/algorithms/maximum-in-list")

    assert response.status_code == 200
    assert response.json()["preconditions"]
    assert response.json()["postconditions"]


def test_unknown_algorithm_returns_not_found() -> None:
    response = client.get("/api/v1/algorithms/missing")

    assert response.status_code == 404


def test_empty_proof_is_rejected_before_engine_invocation() -> None:
    response = client.post(
        "/api/v1/algorithms/maximum-in-list/verify",
        json={"proof_code": ""},
    )

    assert response.status_code == 422


def test_maximum_proof_is_verified_by_lean() -> None:
    response = client.post(
        "/api/v1/algorithms/maximum-in-list/verify",
        json={
            "proof_code": (
                "by\n"
                "  exact member_le_maximumFrom initial value tail membership\n"
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "proved"
    assert response.json()["engine_available"] is True


def test_unformalized_algorithm_returns_conflict() -> None:
    response = client.post(
        "/api/v1/algorithms/linear-search/verify",
        json={"proof_code": "by\n  trivial\n"},
    )

    assert response.status_code == 409


def test_runner_reports_absent_proof_engine() -> None:
    runner = ProofRunner(Settings(lean_command="command-that-does-not-exist"))

    result = runner.verify("theorem smoke_test : True := {{USER_PROOF}}", "by trivial")

    assert result.status == "engine_unavailable"
    assert result.engine_available is False
