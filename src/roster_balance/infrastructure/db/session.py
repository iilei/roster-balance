"""SQLAlchemy engine and session setup."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from collections.abc import Iterator


def get_database_url() -> str:
    return os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg://roster_balance:roster_balance@localhost:5432/roster_balance',
    )


def create_database_engine(database_url: str | None = None) -> Engine:
    return create_engine(database_url or get_database_url(), pool_pre_ping=True)


def create_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    return sessionmaker(
        bind=create_database_engine(database_url),
        class_=Session,
        expire_on_commit=False,
    )


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    with factory.begin() as session:
        yield session
