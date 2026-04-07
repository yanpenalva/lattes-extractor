from datetime import datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.domain.entities import Researcher, ResearcherSummary
from app.interface.deps import (
    get_import_use_case,
    get_list_use_case,
    get_researcher_use_case,
)
from app.main import app

client = TestClient(app)

mock_import_use_case = AsyncMock()
mock_get_use_case = AsyncMock()
mock_list_use_case = AsyncMock()


def override_get_import_use_case():
    return mock_import_use_case


def override_get_researcher_use_case():
    return mock_get_use_case


def override_get_list_use_case():
    return mock_list_use_case


app.dependency_overrides[get_import_use_case] = override_get_import_use_case
app.dependency_overrides[get_researcher_use_case] = override_get_researcher_use_case
app.dependency_overrides[get_list_use_case] = override_get_list_use_case


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Lattes API está funcionando"}


def test_get_researcher_found():
    mock_get_use_case.execute.return_value = Researcher(
        lattes_id="123", name="Test User")

    response = client.get("/api/v1/researchers/123")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"


def test_get_researcher_not_found():
    mock_get_use_case.execute.return_value = None

    response = client.get("/api/v1/researchers/999")
    assert response.status_code == 404


def test_import_researcher_success():
    mock_import_use_case.execute.return_value = Researcher(
        lattes_id="123", name="Test User")

    response = client.post("/api/v1/researchers/import/123")
    assert response.status_code == 200
    assert response.json()["lattes_id"] == "123"


def test_list_researchers():
    mock_list_use_case.execute.return_value = [
        ResearcherSummary(lattes_id="123", name="List User",
                          last_updated=datetime.now())
    ]

    response = client.get("/api/v1/researchers?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "List User"
    assert "publications" not in data[0]
