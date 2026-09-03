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
from app.database.repository import DatabaseRepository


@dataclass
class DatasetRecord:
    dataset_id: str
    name: str
    dataframe: pd.DataFrame | None
    profile: dict
    analysis: dict | None = None
    repaired_dataframe: pd.DataFrame | None = None
    audit: list[dict] = field(default_factory=list)


class PipelineService:
    """Database-independent orchestration for the DataSentinel workflow."""

    def __init__(self, repository: DatabaseRepository | None = None) -> None:
        self._datasets: dict[str, DatasetRecord] = {}
        self.repository = repository or DatabaseRepository()

    def register_file(self, file_path: str | Path, name: str | None = None) -> DatasetRecord:
        dataframe = load_dataset(file_path)
        return self.register_dataframe(dataframe, name or Path(file_path).name)

    def register_dataframe(self, dataframe: pd.DataFrame, name: str) -> DatasetRecord:
        """Persist metadata for an already loaded dataframe."""
        if dataframe is None or dataframe.empty:
            raise ValueError("Dataset must contain at least one row")
        dataset_id = str(uuid4())
        record = DatasetRecord(
            dataset_id=dataset_id,
            name=name,
            dataframe=dataframe,
            profile=profile_dataset(dataframe),
        )
        self.repository.save_dataset(dataset_id, record.name, dataframe, record.profile)
        self._datasets[dataset_id] = record
        return record

    def get(self, dataset_id: str) -> DatasetRecord:
        try:
            return self._datasets[dataset_id]
        except KeyError as exc:
            persisted = self.repository.get_dataset(dataset_id)
            if persisted is not None:
                record = DatasetRecord(dataset_id, persisted["name"], None, persisted["profile"])
                self._datasets[dataset_id] = record
                return record
            raise KeyError(f"Unknown dataset: {dataset_id}") from exc

    def get_analysis(self, dataset_id: str) -> dict | None:
        record = self.get(dataset_id)
        return record.analysis or self.repository.get_analysis(dataset_id)

    def analyze(self, dataset_id: str, config: QualityConfig | None = None) -> dict:
        record = self.get(dataset_id)
        if record.dataframe is None:
            raise ValueError("Dataset data is not loaded in this process")
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
        analysis_id = self.repository.save_analysis(dataset_id, result)
        result["analysis_id"] = analysis_id
        record.analysis = result
        return result

    def repair_duplicates(self, dataset_id: str, approved: bool) -> dict:
        record = self.get(dataset_id)
        if record.dataframe is None:
            raise ValueError("Dataset data is not loaded in this process")
        repaired, result = repair_duplicate_rows(record.dataframe, approved)
        self.repository.save_dataset(dataset_id, record.name, record.dataframe, record.profile)
        audit = create_audit_record(result, len(record.dataframe), len(repaired))
        self.repository.save_repair(dataset_id, record.analysis.get("analysis_id") if record.analysis else None, result)
        if approved:
            record.repaired_dataframe = repaired
        record.audit.append(audit)
        return {"result": result, "audit": audit}

    def validate_latest_repair(self, dataset_id: str) -> dict:
        record = self.get(dataset_id)
        if record.repaired_dataframe is None:
            raise ValueError("No approved repair exists for this dataset")
        validation = validate_repair(record.dataframe, record.repaired_dataframe)
        if record.audit:
            record.audit[-1]["validation"] = validation
        self.repository.update_latest_validation(dataset_id, validation)
        return validation

    def audits(self, dataset_id: str) -> list[dict]:
        record = self.get(dataset_id)
        return record.audit or self.repository.get_audits(dataset_id)


pipeline_service = PipelineService()