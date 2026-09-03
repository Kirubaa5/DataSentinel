# DataSentinel

## AI-Powered Data Quality & Reliability Platform

DataSentinel is an industry-agnostic data quality and reliability platform designed to automatically profile datasets, detect data quality issues, generate findings, score data quality, recommend safe remediation actions, validate repairs, and provide AI-assisted explanations.

> 🚧 **Status: Under Development**

The deterministic backend, FastAPI layer, and PostgreSQL persistence are available
for local testing.
See [docs/architecture.md](docs/architecture.md) and [docs/api.md](docs/api.md)
for the implemented workflow. PostgreSQL, RAG, LLM, and frontend work are
deliberately deferred to later phases. Set `DATABASE_URL` in `backend/.env` before
starting the API.

---

## 🎯 Project Goal

Build a production-oriented platform that can take a raw tabular dataset and transform it into actionable data quality insights.

The core data quality engine is deterministic and rule-based. AI, RAG, and LLM capabilities will be layered on top of the quality engine rather than replacing deterministic validation.

---

## 🏗️ Planned Architecture

```text
Data Source
    ↓
Ingestion
    ↓
Profiling
    ↓
Quality Engine
    ↓
Findings
    ↓
Anomaly Detection
    ↓
Quality Scoring
    ↓
Rule Engine
    ↓
Repair / Remediation
    ↓
Validation
    ↓
RAG + LLM
    ↓
User Interface