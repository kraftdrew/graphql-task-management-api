"""Shared SQLAlchemy declarative base and model mixins."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all database models."""
