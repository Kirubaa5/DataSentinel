from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.core.config import QualityConfig
from app.findings.generator import generate_findings
from app.ingestion.loaders import load_dataset
from app.profiling.profiler import profile_dataset
from app.quality.anomaly import detect_anomalies
from app.quality.engine import run_quality_checks
from app.repair.audit import create_audit_record
from app.repair.repair_engine import repair_duplicate_rows
from app.repair.recommendations import generate_recommendations
from app.rules.rule_engine import apply_business_rules
from app.scoring.quality_score import calculate_quality_score
from app.validation.validator import validate_repair


@dataclass
class DatasetRecord:
    dataset_id: str
    name: str
    dataframe: pd.DataFrame
    profile: dict
    analysis: dict | None = None
    repaired_dataframe: pd.DataFrame | None = None
    audit: list[dict] = field(default_factory=list)


class PipelineService:
    """Database-independent orchestration for the DataSentinel workflow."""

    def __init__(self) -> None:
        self._datasets: dict[str, DatasetRecord] = {}

    def register_file(self, file_path: str | Path, name: str | None = None) -> DatasetRecord:
        dataframe = load_dataset(file_path)
        dataset_id = str(uuid4())
        record = DatasetRecord(
            dataset_id=dataset_id,
            name=name or Path(file_path).name,
            dataframe=dataframe,
            profile=profile_dataset(dataframe),
        )
        self._datasets[dataset_id] = record
        return record

    def get(self, dataset_id: str) -> DatasetRecord:
        try:
            return self._datasets[dataset_id]
        except KeyError as exc:
            raise KeyError(f"Unknown dataset: {dataset_id}") from exc

    def analyze(self, dataset_id: str, config: QualityConfig | None = None) -> dict:
        record = self.get(dataset_id)
        quality = run_quality_checks(record.dataframe, config)
        anomaly_results = []
        for column in (config.anomaly_columns if config else ()):
            anomaly_results.append(
                detect_anomalies(
                    record.dataframe,
                    column,
                    config.anomaly_contamination if config else 0.01,
                )
            )
        quality["anomalies"] = anomaly_results
        findings = generate_findings(quality)
        business_rules = apply_business_rules(record.dataframe)
        score = calculate_quality_score(findings)
        result = {
            "dataset_id": dataset_id,
            "profile": record.profile,
            "quality_results": quality,
            "findings": findings,
            "business_rules": business_rules,
            "score": score,
            "recommendations": generate_recommendations(findings, business_rules),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        record.analysis = result
        return result

    def repair_duplicates(self, dataset_id: str, approved: bool) -> dict:
        record = self.get(dataset_id)
        repaired, result = repair_duplicate_rows(record.dataframe, approved)
        if approved:
            record.repaired_dataframe = repaired
        audit = create_audit_record(result, len(record.dataframe), len(repaired))
        record.audit.append(audit)
        return {"result": result, "audit": audit}

    def validate_latest_repair(self, dataset_id: str) -> dict:
        record = self.get(dataset_id)
        if record.repaired_dataframe is None:
            raise ValueError("No approved repair exists for this dataset")
        validation = validate_repair(record.dataframe, record.repaired_dataframe)
        if record.audit:
            record.audit[-1]["validation"] = validation
        return validation

    def audits(self, dataset_id: str) -> list[dict]:
        return self.get(dataset_id).audit


pipeline_service = PipelineService()