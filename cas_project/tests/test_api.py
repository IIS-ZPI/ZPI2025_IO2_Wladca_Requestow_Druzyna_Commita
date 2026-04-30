import pytest
import requests
from unittest.mock import patch
from api import fetch_currency_data

@patch("api.requests.get")
def test_fetch_currency_data_success(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
         "rates": [{"mid": 4.12}, {"mid": 4.15}]
    }
    
    data = fetch_currency_data("USD", 1)
    
    assert len(data) == 2
    assert data[0] == 4.12
    assert data[1] == 4.15

@patch("api.requests.get")
def test_fetch_currency_data_not_found(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 404
    
    data = fetch_currency_data("WRONG", 5)
    
    assert data == []

@patch("api.requests.get")
def test_fetch_currency_data_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
    
    with pytest.raises(Exception) as excinfo:
         fetch_currency_data("USD", 5)
         
    assert "API Error fetching data" in str(excinfo.value)
