from fastapi import APIRouter, HTTPException

from app.services.pipeline import pipeline_service

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["results"])


def _analysis(dataset_id: str) -> dict:
    try:
        result = pipeline_service.get(dataset_id).analysis
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis has not been run")
    return result


@router.get("/findings")
def get_findings(dataset_id: str) -> list[dict]:
    return _analysis(dataset_id)["findings"]


@router.get("/score")
def get_score(dataset_id: str) -> dict:
    return _analysis(dataset_id)["score"]


@router.get("/recommendations")
def get_recommendations(dataset_id: str) -> list[dict]:
    return _analysis(dataset_id)["recommendations"]