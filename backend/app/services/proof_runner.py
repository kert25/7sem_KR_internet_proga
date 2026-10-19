"""Controlled execution boundary for Lean proof verification."""

from __future__ import annotations

import shlex
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings


@dataclass(frozen=True)
class ProofRunResult:
    """Result returned by the Lean execution boundary."""

    status: str
    duration_ms: int
    diagnostic: str
    engine_available: bool


class ProofRunner:
    """Build and run one Lean file without interpreting user input as a shell command."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def verify(self, template: str, proof_code: str) -> ProofRunResult:
        """Insert a proof block into an approved template and invoke Lean."""

        marker = "{{USER_PROOF}}"
        if template.count(marker) != 1:
            raise ValueError("Шаблон доказательства должен содержать один маркер вставки.")
        if len(proof_code) > self._settings.proof_source_limit:
            raise ValueError("Размер доказательства превышает допустимый предел.")

        source = template.replace(marker, proof_code)
        command = shlex.split(self._settings.lean_command)
        started = time.perf_counter()

        try:
            with tempfile.TemporaryDirectory(prefix="proof-run-") as directory:
                source_path = Path(directory) / "Proof.lean"
                source_path.write_text(source, encoding="utf-8")
                completed = subprocess.run(
                    [*command, str(source_path)],
                    cwd=self._settings.lean_project_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=self._settings.proof_timeout_seconds,
                    check=False,
                    shell=False,
                )
        except FileNotFoundError:
            return ProofRunResult(
                status="engine_unavailable",
                duration_ms=self._duration_ms(started),
                diagnostic=(
                    "Lean 4 не установлен или команда proof engine недоступна. "
                    "Установите Lean 4 и настройте LEAN_COMMAND."
                ),
                engine_available=False,
            )
        except subprocess.TimeoutExpired:
            return ProofRunResult(
                status="timeout",
                duration_ms=self._duration_ms(started),
                diagnostic="Превышено допустимое время проверки доказательства.",
                engine_available=True,
            )

        diagnostic = (completed.stdout + completed.stderr).strip()
        if completed.returncode == 0:
            return ProofRunResult(
                status="proved",
                duration_ms=self._duration_ms(started),
                diagnostic=diagnostic or "Доказательство успешно проверено Lean 4.",
                engine_available=True,
            )
        return ProofRunResult(
            status="not_proved",
            duration_ms=self._duration_ms(started),
            diagnostic=diagnostic or "Lean 4 не смог подтвердить доказательство.",
            engine_available=True,
        )

    @staticmethod
    def _duration_ms(started: float) -> int:
        return round((time.perf_counter() - started) * 1000)
