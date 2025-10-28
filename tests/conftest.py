from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.database import get_session, init_db
from app.main import app
from app.seed import create_demo_data


@pytest.fixture(scope="session", autouse=True)
def _cleanup_database() -> Iterator[None]:
    if os.path.exists("stocky.db"):
        os.remove("stocky.db")
    init_db()
    with get_session() as session:
        create_demo_data(session)
    yield
    if os.path.exists("stocky.db"):
        os.remove("stocky.db")


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
