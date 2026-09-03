import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.ingestion.loaders import load_dataset
from app.main import app
from app.profiling.profiler import profile_dataset
from app.services.pipeline import DatasetRecord, PipelineService


def test_pipeline_repairs_only_after_approval() -> None:
    service = PipelineService()
    dataframe = pd.DataFrame({"value": [1, 1, 2], "label": ["a", "a", "b"]})
    service._datasets["test"] = DatasetRecord("test", "test.csv", dataframe, profile_dataset(dataframe))

    pending = service.repair_duplicates("test", approved=False)
    assert pending["result"]["changed"] is False
    approved = service.repair_duplicates("test", approved=True)
    assert approved["result"]["removed_count"] == 1
    assert service.validate_latest_repair("test")["validation_passed"] is True


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_empty_dataset_is_rejected(tmp_path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("value\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no rows"):
        load_dataset(csv_path)


def test_api_upload_analysis_and_results(tmp_path) -> None:
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"value": [1, 1, 2]}).to_csv(csv_path, index=False)
    client = TestClient(app)
    with csv_path.open("rb") as file_handle:
        upload = client.post("/api/datasets", files={"file": ("sample.csv", file_handle, "text/csv")})
    assert upload.status_code == 201
    dataset_id = upload.json()["dataset_id"]
    analysis = client.post(f"/api/datasets/{dataset_id}/analysis", json={})
    assert analysis.status_code == 200
    assert client.get(f"/api/datasets/{dataset_id}/score").json()["score"] < 100