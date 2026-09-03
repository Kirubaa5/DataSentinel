from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.pipeline import pipeline_service

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", status_code=201)
async def upload_dataset(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded dataset is empty")
    try:
        with NamedTemporaryFile(suffix=suffix, delete=False) as temporary:
            temporary.write(contents)
            path = temporary.name
        record = pipeline_service.register_file(path, file.filename)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if "path" in locals():
            Path(path).unlink(missing_ok=True)
    return {"dataset_id": record.dataset_id, "name": record.name, "profile": record.profile}


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str) -> dict:
    try:
        record = pipeline_service.get(dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"dataset_id": record.dataset_id, "name": record.name, "profile": record.profile}