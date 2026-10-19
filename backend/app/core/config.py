"""Runtime configuration for the API service."""

from functools import lru_cache
from pathlib import Path
from shutil import which
import shlex

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _default_lean_command() -> str:
    """Find Lake in PATH or in elan's standard per-user installation path."""

    lake_in_path = which("lake")
    if lake_in_path:
        return f"{shlex.quote(lake_in_path)} env lean"

    elan_lake = Path.home() / ".elan" / "bin" / "lake.exe"
    if elan_lake.is_file():
        return f"{shlex.quote(str(elan_lake))} env lean"
    return "lake env lean"


class Settings(BaseSettings):
    """Application settings loaded from environment variables when present."""

    app_name: str = "Algorithm Correctness Prover"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
    lean_command: str = _default_lean_command()
    lean_project_dir: Path = PROJECT_ROOT / "lean"
    proof_timeout_seconds: int = 10
    proof_source_limit: int = 20_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the process."""

    return Settings()
