import pandas as pd

from app.database.connection import create_tables
from app.services.pipeline import PipelineService


def test_postgres_persists_pipeline_artifacts() -> None:
    create_tables()
    service = PipelineService()
    dataframe = pd.DataFrame({"value": [1, 1, 2]})
    record = service.register_dataframe(dataframe, "db-test")
    analysis = service.analyze(record.dataset_id)
    service.repair_duplicates(record.dataset_id, approved=True)
    validation = service.validate_latest_repair(record.dataset_id)

    restarted = PipelineService()
    assert restarted.get(record.dataset_id).profile["row_count"] == 3
    assert restarted.get_analysis(record.dataset_id)["score"] == analysis["score"]
    assert restarted.audits(record.dataset_id)[0]["approved"] is True
    assert validation["validation_passed"] is True