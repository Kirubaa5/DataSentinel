from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Analysis, AuditLog, Dataset, Finding, QualityScore, Repair


class PersistenceError(RuntimeError):
    """Raised when a persistence operation cannot be committed."""


class DatabaseRepository:
    """Persistence adapter for pipeline artifacts and dataset metadata."""

    def __init__(self, session_factory=SessionLocal) -> None:
        self.session_factory = session_factory

    def _commit(self, session: Session) -> None:
        try:
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            raise PersistenceError("Database transaction failed") from exc

    def save_dataset(self, dataset_id: str, filename: str, dataframe, profile: dict) -> None:
        session = self.session_factory()
        try:
            session.merge(Dataset(
                id=dataset_id,
                filename=filename,
                file_type=Path(filename).suffix.lower().lstrip("."),
                row_count=profile["row_count"],
                column_count=profile["column_count"],
                profile=profile,
            ))
            self._commit(session)
        finally:
            session.close()

    def get_dataset(self, dataset_id: str) -> dict | None:
        session = self.session_factory()
        try:
            row = session.get(Dataset, dataset_id)
            if row is None:
                return None
            return {
                "dataset_id": row.id,
                "name": row.filename,
                "profile": row.profile,
                "status": row.status,
                "version": row.version,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
        finally:
            session.close()

    def save_analysis(self, dataset_id: str, result: dict) -> str:
        analysis_id = str(uuid4())
        session = self.session_factory()
        try:
            analysis = Analysis(
                id=analysis_id,
                dataset_id=dataset_id,
                status="completed",
                completed_at=datetime.now(timezone.utc),
                result=result,
            )
            session.add(analysis)
            for finding in result["findings"]:
                session.add(Finding(
                    id=f"{analysis_id}:{finding['finding_id']}",
                    analysis_id=analysis_id,
                    check=finding["check"],
                    column=finding.get("column"),
                    issue=finding["issue"],
                    severity=finding["severity"],
                    count=finding["count"],
                    percentage=finding.get("percentage"),
                    details=finding["details"],
                ))
            score = result["score"]
            session.add(QualityScore(
                analysis_id=analysis_id,
                score=score["score"],
                grade=score["grade"],
                penalty=score["total_penalty"],
                severity_counts=score["severity_counts"],
            ))
            self._commit(session)
            return analysis_id
        finally:
            session.close()

    def get_analysis(self, dataset_id: str) -> dict | None:
        session = self.session_factory()
        try:
            row = session.scalars(
                select(Analysis).where(Analysis.dataset_id == dataset_id).order_by(Analysis.started_at.desc())
            ).first()
            return row.result if row else None
        finally:
            session.close()

    def save_repair(self, dataset_id: str, analysis_id: str | None, result: dict) -> str:
        repair_id = str(uuid4())
        session = self.session_factory()
        try:
            repair = Repair(
                id=repair_id,
                dataset_id=dataset_id,
                analysis_id=analysis_id,
                repair_type=result["repair"],
                approved=result["approved"],
                changed=result["changed"],
                removed_count=result.get("removed_count", 0),
                before_state=result.get("before", {}),
                after_state=result.get("after", {}),
            )
            session.add(repair)
            session.flush()
            session.add(AuditLog(
                id=str(uuid4()),
                dataset_id=dataset_id,
                repair_id=repair_id,
                action=result["repair"],
                approved=result["approved"],
                changed=result["changed"],
                before_rows=result.get("before", {}).get("rows", 0),
                after_rows=result.get("after", {}).get("rows", 0),
                details=result,
            ))
            self._commit(session)
            return repair_id
        finally:
            session.close()

    def update_latest_validation(self, dataset_id: str, validation: dict) -> None:
        session = self.session_factory()
        try:
            audit = session.scalars(
                select(AuditLog).where(AuditLog.dataset_id == dataset_id).order_by(AuditLog.created_at.desc())
            ).first()
            if audit is not None:
                audit.details = {**audit.details, "validation": validation}
                self._commit(session)
        finally:
            session.close()

    def get_audits(self, dataset_id: str) -> list[dict]:
        session = self.session_factory()
        try:
            rows = session.scalars(
                select(AuditLog).where(AuditLog.dataset_id == dataset_id).order_by(AuditLog.created_at.asc())
            ).all()
            return [
                {
                    "timestamp": row.created_at.isoformat() if row.created_at else None,
                    "repair": row.action,
                    "approved": row.approved,
                    "changed": row.changed,
                    "before_rows": row.before_rows,
                    "after_rows": row.after_rows,
                    "removed_count": row.details.get("removed_count", 0),
                    "before": row.details.get("before"),
                    "after": row.details.get("after"),
                    "validation": row.details.get("validation"),
                    "message": row.details.get("message"),
                }
                for row in rows
            ]
        finally:
            session.close()