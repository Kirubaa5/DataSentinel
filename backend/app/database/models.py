from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.connection import Base


class Dataset(Base):
	__tablename__ = "datasets"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	filename: Mapped[str] = mapped_column(String(255), nullable=False)
	file_type: Mapped[str] = mapped_column(String(16), nullable=False)
	row_count: Mapped[int] = mapped_column(Integer, nullable=False)
	column_count: Mapped[int] = mapped_column(Integer, nullable=False)
	profile: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
	version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	analyses: Mapped[list["Analysis"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class Analysis(Base):
	__tablename__ = "analyses"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
	started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

	dataset: Mapped[Dataset] = relationship(back_populates="analyses")
	findings: Mapped[list["Finding"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
	score: Mapped["QualityScore | None"] = relationship(back_populates="analysis", cascade="all, delete-orphan", uselist=False)
	repairs: Mapped[list["Repair"]] = relationship(back_populates="analysis", cascade="all, delete-orphan")


class Finding(Base):
	__tablename__ = "findings"
	__table_args__ = (Index("ix_findings_analysis_severity", "analysis_id", "severity"),)

	id: Mapped[str] = mapped_column(String(128), primary_key=True)
	analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
	check: Mapped[str] = mapped_column(String(64), nullable=False)
	column: Mapped[str | None] = mapped_column(String(255))
	issue: Mapped[str] = mapped_column(String(128), nullable=False)
	severity: Mapped[str] = mapped_column(String(16), nullable=False)
	count: Mapped[int] = mapped_column(Integer, nullable=False)
	percentage: Mapped[float | None] = mapped_column()
	details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

	analysis: Mapped[Analysis] = relationship(back_populates="findings")


class QualityScore(Base):
	__tablename__ = "quality_scores"

	analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), primary_key=True)
	score: Mapped[int] = mapped_column(Integer, nullable=False)
	grade: Mapped[str] = mapped_column(String(16), nullable=False)
	penalty: Mapped[int] = mapped_column(Integer, nullable=False)
	severity_counts: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

	analysis: Mapped[Analysis] = relationship(back_populates="score")


class Repair(Base):
	__tablename__ = "repairs"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
	analysis_id: Mapped[str | None] = mapped_column(ForeignKey("analyses.id", ondelete="SET NULL"))
	repair_type: Mapped[str] = mapped_column(String(64), nullable=False)
	approved: Mapped[bool] = mapped_column(nullable=False, default=False)
	changed: Mapped[bool] = mapped_column(nullable=False, default=False)
	removed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	before_state: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	after_state: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	analysis: Mapped[Analysis | None] = relationship(back_populates="repairs")


class AuditLog(Base):
	__tablename__ = "audit_logs"
	__table_args__ = (Index("ix_audit_logs_dataset_created", "dataset_id", "created_at"),)

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
	repair_id: Mapped[str | None] = mapped_column(ForeignKey("repairs.id", ondelete="SET NULL"))
	action: Mapped[str] = mapped_column(String(64), nullable=False)
	approved: Mapped[bool] = mapped_column(nullable=False, default=False)
	changed: Mapped[bool] = mapped_column(nullable=False, default=False)
	before_rows: Mapped[int] = mapped_column(Integer, nullable=False)
	after_rows: Mapped[int] = mapped_column(Integer, nullable=False)
	details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
