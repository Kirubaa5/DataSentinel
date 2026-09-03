from fastapi import APIRouter, HTTPException

from app.core.config import QualityConfig
from app.api.schemas import AnalysisRequest
from app.services.pipeline import pipeline_service

router = APIRouter(prefix="/datasets/{dataset_id}/analysis", tags=["analysis"])


@router.post("")
def run_analysis(dataset_id: str, request: AnalysisRequest | None = None) -> dict:
    request = request or AnalysisRequest()
    config = QualityConfig(
        anomaly_columns=tuple(request.anomaly_columns),
        anomaly_contamination=request.anomaly_contamination,
        numeric_constraints=request.numeric_constraints,
        format_rules=request.format_rules,
        consistency_columns=tuple(request.consistency_columns),
    )
    try:
        return pipeline_service.analyze(dataset_id, config)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def get_analysis(dataset_id: str) -> dict:
    try:
        result = pipeline_service.get(dataset_id).analysis
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis has not been run")
    return result