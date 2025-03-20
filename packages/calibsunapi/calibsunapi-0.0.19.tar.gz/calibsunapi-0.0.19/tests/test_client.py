from datetime import time
from unittest.mock import MagicMock, patch

import pytest

from calibsunapi.client import CalibsunApiClient
from calibsunapi.exceptions import NoCredentialsError, NotAuthenticatedError
from calibsunapi.models.listplants import Plant
from calibsunapi.models.uploadmeasurements import UploadMeasurementsFormats


@patch("calibsunapi.client.requests.post")
def test_authenticate_success(mock_post, client: CalibsunApiClient):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test_token", "expires_in": 3600, "token_type": "Bearer"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    client._authenticate()

    assert client._token is not None
    assert client._token.access_token == "test_token"


@patch("calibsunapi.client.requests.post")
def test_authenticate_no_credentials(mock_post):
    client = CalibsunApiClient()
    print(client.calibsun_client_id)
    with pytest.raises(NoCredentialsError):
        client._authenticate()


@patch("calibsunapi.client.requests.get")
def test_list_plants(mock_get, authentified_client: CalibsunApiClient, plant):
    mock_response = MagicMock()
    site_id = plant.pop("site_id")
    mock_response.json.return_value = {site_id: plant}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    plants = authentified_client.list_plants()

    assert len(plants) == 1
    assert isinstance(plants[0], Plant)
    assert plants[0].site_id == site_id


@patch("calibsunapi.client.requests.post")
@patch("calibsunapi.client.requests.get")
def test_push_measurements(mock_get, mock_post, authentified_client: CalibsunApiClient):
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {"url": "http://example.com/upload", "fields": {"field1": "value1"}}
    mock_get_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_get_response

    mock_post_response = MagicMock()
    mock_post_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_post_response

    response = authentified_client.push_measurements("site_id", UploadMeasurementsFormats.JSON, data={"key": "value"})

    assert response.raise_for_status.called


@patch("calibsunapi.client.requests.get")
def test_get_latest_forecast(mock_get, authentified_client: CalibsunApiClient):
    mock_response = MagicMock()
    mock_response.json.return_value = {"forecast": "data"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    forecast = authentified_client.get_latest_forecast("site_id", "target")

    assert forecast == {"forecast": "data"}


@patch("calibsunapi.client.requests.get")
def test_get_latest_forecast_probabilistic(mock_get, authentified_client: CalibsunApiClient):
    mock_response = MagicMock()
    mock_response.json.return_value = {"forecast": "probabilistic_data"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    forecast = authentified_client.get_latest_forecast_probabilistic("site_id", "target")

    assert forecast == {"forecast": "probabilistic_data"}


@patch("calibsunapi.client.requests.get")
def test_get_latest_forecast_deterministic(mock_get, authentified_client: CalibsunApiClient):
    mock_response = MagicMock()
    mock_response.json.return_value = {"forecast": "deterministic_data"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    forecast = authentified_client.get_latest_forecast_deterministic("site_id", "target")

    assert forecast == {"forecast": "deterministic_data"}


@patch("calibsunapi.client.requests.get")
def test_get_forecast(mock_get, authentified_client: CalibsunApiClient):
    mock_response = MagicMock()
    mock_response.json.return_value = {"forecast": "fixed_time_data"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    forecast = authentified_client.get_forecast(time(0, 0), "site_id", "target")

    assert forecast == {"forecast": "fixed_time_data"}
