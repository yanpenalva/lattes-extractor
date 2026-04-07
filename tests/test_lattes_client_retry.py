from unittest.mock import MagicMock, patch

import pytest
from tenacity import wait_none

from app.infrastructure.external.lattes_client import LattesClient

LattesClient.get_curriculum_zip.retry.wait = wait_none()


@pytest.fixture
def lattes_client():
    with patch("app.infrastructure.external.lattes_client.zeep.Client") as mock_zeep:
        instance = LattesClient()
        mock_service = MagicMock()
        mock_zeep.return_value.service = mock_service
        instance._client = mock_zeep.return_value
        yield instance


def test_returns_data_on_first_attempt(lattes_client):
    lattes_client.client.service.getCurriculoCompactado = MagicMock(
        return_value=b"zip_data")

    result = lattes_client.get_curriculum_zip("1234567890")

    assert result == b"zip_data"
    lattes_client.client.service.getCurriculoCompactado.assert_called_once_with(
        "1234567890")


def test_retries_on_failure_and_succeeds(lattes_client):
    lattes_client.client.service.getCurriculoCompactado = MagicMock(
        side_effect=[Exception("timeout"), Exception("timeout"), b"zip_data"]
    )

    result = lattes_client.get_curriculum_zip("1234567890")

    assert result == b"zip_data"
    assert lattes_client.client.service.getCurriculoCompactado.call_count == 3


def test_reraises_after_max_attempts(lattes_client):
    lattes_client.client.service.getCurriculoCompactado = MagicMock(
        side_effect=Exception("CNPq unavailable")
    )

    with pytest.raises(Exception, match="CNPq unavailable"):
        lattes_client.get_curriculum_zip("1234567890")

    assert lattes_client.client.service.getCurriculoCompactado.call_count == 3
