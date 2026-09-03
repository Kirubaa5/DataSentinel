from fastapi import APIRouter, HTTPException

from app.api.schemas import RepairRequest
from app.services.pipeline import pipeline_service

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["repairs"])


@router.post("/repairs/duplicates")
def repair_duplicates(dataset_id: str, request: RepairRequest) -> dict:
    try:
        return pipeline_service.repair_duplicates(dataset_id, request.approved)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/repairs/validate")
def validate_repair(dataset_id: str) -> dict:
    try:
        return pipeline_service.validate_latest_repair(dataset_id)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/audit")
def get_audit(dataset_id: str) -> list[dict]:
    try:
        return pipeline_service.audits(dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc