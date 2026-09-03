 # DataSentinel Backend Architecture

The current backend is database-independent and deterministic. `PipelineService`
coordinates ingestion, profiling, configured quality checks, optional Isolation
Forest evidence, findings, business-rule classification, scoring, recommendations,
approval-based repair, validation, and audit. The FastAPI layer only translates
HTTP requests into service calls; raw data is never modified by a repair.

Quality checks are generic and configuration-driven. Business rules are a separate
classification stage, so statistical anomalies, outliers, and constraint findings
are not treated as errors automatically. PostgreSQL, RAG, and LLM components remain
future layers.

## Run

From the repository root:

```powershell
$env:PYTHONPATH = "backend"
uvicorn app.main:app --app-dir backend --reload
```

## Workflow

1. Upload CSV/XLSX with `POST /api/datasets`.
2. Inspect the profile with `GET /api/datasets/{dataset_id}`.
3. Run analysis with `POST /api/datasets/{dataset_id}/analysis`.
4. Retrieve findings, score, and recommendations from their result endpoints.
5. Submit explicit approval to `POST /api/datasets/{dataset_id}/repairs/duplicates`.
6. Validate with `POST /api/datasets/{dataset_id}/repairs/validate` and inspect audit.

PostgreSQL now stores dataset metadata, profiles, analyses, findings, scores,
repairs, and audit logs through `DatabaseRepository`. The dataframe itself remains
in the file-processing workflow and is never stored in PostgreSQL. Tables are
bootstrapped with SQLAlchemy `Base.metadata.create_all()` during API startup; a
versioned Alembic migration can replace this bootstrap when deployment environments
need schema history. After a restart, persisted metadata and analysis results are
available, but repair or re-analysis requires the source dataframe to be loaded
again because raw data is intentionally not persisted.
