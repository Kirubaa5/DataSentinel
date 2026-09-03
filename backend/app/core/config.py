from dataclasses import dataclass, field


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
