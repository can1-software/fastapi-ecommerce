"""SQLAlchemy declarative base — Alembic target_metadata için."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Tüm ORM modellerinin türeyeceği taban sınıf."""
