from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import database_url


class Base(DeclarativeBase):
	"""Base class for persistence models."""


engine = create_engine(database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
	"""Yield a transactional session for API or service use."""
	session = SessionLocal()
	try:
		yield session
	except Exception:
		session.rollback()
		raise
	finally:
		session.close()


def create_tables() -> None:
	"""Create missing tables for the initial local deployment."""
	from app.database import models  # noqa: F401

	Base.metadata.create_all(bind=engine)
