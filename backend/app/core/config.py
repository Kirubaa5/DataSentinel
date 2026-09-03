import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv() -> None:
	"""Load simple KEY=VALUE settings without adding a dotenv dependency."""
	env_path = Path(__file__).resolve().parents[2] / ".env"
	if not env_path.exists():
		return
	for line in env_path.read_text(encoding="utf-8").splitlines():
		line = line.strip()
		if line and not line.startswith("#") and "=" in line:
			key, value = line.split("=", 1)
			os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def database_url() -> str:
	"""Return the configured SQLAlchemy database URL."""
	value = os.getenv("DATABASE_URL")
	if not value:
		raise ValueError("DATABASE_URL is not configured")
	if value.startswith("postgresql://"):
		return value.replace("postgresql://", "postgresql+psycopg://", 1)
	if value.startswith("postgres://"):
		return value.replace("postgres://", "postgresql+psycopg://", 1)
	return value


@dataclass(frozen=True)
class QualityConfig:
	"""Configuration for deterministic checks and optional anomaly detection."""

	anomaly_columns: tuple[str, ...] = ()
	anomaly_contamination: float = 0.01
	numeric_constraints: dict[str, dict] = field(default_factory=dict)
	format_rules: dict[str, dict] = field(default_factory=dict)
	consistency_columns: tuple[str, ...] = ()

	def __post_init__(self) -> None:
		if not 0 < self.anomaly_contamination <= 0.5:
			raise ValueError("anomaly_contamination must be greater than 0 and at most 0.5")
