 # API Reference

All dataset routes are under `/api`. Responses are JSON.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health |
| POST | `/api/datasets` | Upload CSV/XLSX as multipart field `file` |
| GET | `/api/datasets/{id}` | Dataset metadata and profile |
| POST | `/api/datasets/{id}/analysis` | Run configured deterministic analysis |
| GET | `/api/datasets/{id}/analysis` | Retrieve the latest analysis |
| GET | `/api/datasets/{id}/findings` | Retrieve findings |
| GET | `/api/datasets/{id}/score` | Retrieve deterministic score and grade |
| GET | `/api/datasets/{id}/recommendations` | Retrieve safe recommendations |
| POST | `/api/datasets/{id}/repairs/duplicates` | Request duplicate repair; body is `{"approved": true}` |
| POST | `/api/datasets/{id}/repairs/validate` | Validate the latest approved repair |
| GET | `/api/datasets/{id}/audit` | Retrieve repair audit records |

Analysis configuration may include `anomaly_columns`, `anomaly_contamination`,
`numeric_constraints`, `format_rules`, and `consistency_columns`. Repairs are
never applied unless approval is explicitly true, and the original dataframe is
retained in memory.
