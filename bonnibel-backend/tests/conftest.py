"""Wspólne fixtury testowe: izolowana baza SQLite in-memory na naszych core/models."""
from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.models import Base, User, UserStatus


# W SQLite autoinkrementacja działa tylko dla "INTEGER PRIMARY KEY" (alias ROWID),
# a nasze PK to BigInteger -> BIGINT. Na potrzeby testów kompilujemy BigInteger
# jako INTEGER (tylko dialekt sqlite; produkcyjny Postgres bez zmian).
@compiles(BigInteger, "sqlite")
def _compile_bigint_sqlite(element, compiler, **kw):  # noqa: ANN001
    return "INTEGER"


@pytest.fixture
def db():
    # StaticPool + jedno połączenie => baza :memory: żyje przez cały test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def run():
    """Uruchamia korutynę serwisu w teście synchronicznym."""
    def _run(coro):
        return asyncio.run(coro)
    return _run


@pytest.fixture
def make_user(db):
    def _make(user_id: str, email: str) -> User:
        user = User(
            user_id=user_id,
            email=email,
            name=user_id,
            surname="Test",
            status=UserStatus.ACTIVE,
            is_online=False,
        )
        db.add(user)
        db.commit()
        return user
    return _make
