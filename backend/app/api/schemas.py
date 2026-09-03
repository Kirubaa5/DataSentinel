from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    anomaly_columns: list[str] = Field(default_factory=list)
    anomaly_contamination: float = Field(default=0.01, gt=0, le=0.5)
    numeric_constraints: dict[str, dict] = Field(default_factory=dict)
    format_rules: dict[str, dict] = Field(default_factory=dict)
    consistency_columns: list[str] = Field(default_factory=list)


class RepairRequest(BaseModel):
    approved: bool = False