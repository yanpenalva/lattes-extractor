import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client_app():
    with TestClient(app) as c:
        yield c
