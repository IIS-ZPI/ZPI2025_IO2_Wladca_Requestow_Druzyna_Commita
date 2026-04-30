import pytest
import requests
import math
from unittest.mock import patch
from api import fetch_currency_data

# =====================================================================
# BLOCK 1: PRE-FLIGHT INPUT MUTILATION (10 Tests)
# These test if api.py validates inputs BEFORE building the URL.
# CURRENT BUG: api.py blindly does `count = sessions + 1` and string interpolation.
# =====================================================================

PRE_FLIGHT_PAYLOADS = [
    # (currency, sessions, expected_exception)
    (None, 5, TypeError),  # Concatenating None into string URL
    ("USD", None, TypeError),  # None + 1 throws TypeError
    ("USD", "5", TypeError),  # String + 1 throws TypeError
    ("USD", [5], TypeError),  # List + 1 throws TypeError
    ("USD", {"num": 5}, TypeError),  # Dict + 1 throws TypeError
    ("USD", math.nan, Exception),  # URL becomes /last/nan/ (HTTP 400 from NBP)
    ("USD", math.inf, Exception),  # URL becomes /last/inf/ (HTTP 400 from NBP)
    ("USD", -5, Exception),  # URL becomes /last/-4/ (HTTP 400 from NBP)
    ("", 5, Exception),  # Empty currency -> /rates/A//last/6/ (HTTP 404)
    ("🇺🇸USD", 5, Exception),  # Unicode emoji might break naive URL encoders
]


@pytest.mark.parametrize("curr, sess, exc", PRE_FLIGHT_PAYLOADS)
@patch("api.requests.get")
def test_pre_flight_input_fuzzing(mock_get, curr, sess, exc):
    """Testing vulnerability to bad argument types before HTTP execution."""
    # Mocking a bad request response for cases where the bad URL actually gets sent
    mock_get.return_value.status_code = 400
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()

    with pytest.raises(exc):
        fetch_currency_data(curr, sess)


# =====================================================================
# BLOCK 2: NETWORK INFRASTRUCTURE FAILURES (5 Tests)
# These test if socket-level drops and deep network errors are caught.
# =====================================================================

NETWORK_FAILURES = [
    requests.exceptions.ConnectionError("DNS Resolution failed"),
    requests.exceptions.ReadTimeout("Server stalled"),
    requests.exceptions.SSLError("Invalid certificate"),
    requests.exceptions.ProxyError("Corporate proxy blocked"),
    requests.exceptions.ChunkedEncodingError("Stream broken mid-download"),
]


@pytest.mark.parametrize("exception_type", NETWORK_FAILURES)
@patch("api.requests.get")
def test_network_layer_failures(mock_get, exception_type):
    """Testing deep network stack failures."""
    mock_get.side_effect = exception_type
    with pytest.raises(Exception, match="API Error fetching data"):
        fetch_currency_data("USD", 5)


# =====================================================================
# BLOCK 3: OBSCURE HTTP STATUS CODES (5 Tests)
# Testing if raise_for_status() properly catches non-200/404 codes.
# =====================================================================

HTTP_STATUS_CODES = [
    (500, "Internal Server Error"),
    (502, "Bad Gateway"),
    (504, "Gateway Timeout"),
    (429, "Too Many Requests"),
    (403, "Forbidden"),
]


@pytest.mark.parametrize("code, reason", HTTP_STATUS_CODES)
@patch("api.requests.get")
def test_http_status_code_anomalies(mock_get, code, reason):
    """Testing server-side HTTP rejection codes."""
    mock_response = mock_get.return_value
    mock_response.status_code = code
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{code} {reason}")

    with pytest.raises(Exception, match="API Error fetching data"):
        fetch_currency_data("USD", 5)


# =====================================================================
# BLOCK 4: JSON SCHEMA POISONING - CRASHES (15 Tests)
# These simulate NBP changing their API format or returning corrupted JSON.
# CURRENT BUG: api.py blindly accesses `data['rates']` and `item['mid']`.
# =====================================================================

FATAL_JSON_PAYLOADS = [
    # 1. Structural anomalies (Not dictionaries)
    ([], TypeError),
    ("Not JSON", TypeError),
    (1234, TypeError),

    # 2. Missing root keys
    ({}, KeyError),
    ({"table": "A", "currency": "USD"}, KeyError),  # Missing 'rates'
    ({"RATES": [{"mid": 4.1}]}, KeyError),  # Case sensitive failure

    # 3. 'rates' is present but wrong type
    ({"rates": None}, TypeError),
    ({"rates": "Unavailable"}, TypeError),
    ({"rates": {"date": 4.1}}, TypeError),  # Dict instead of list

    # 4. 'rates' is a list, but items are wrong type
    ({"rates": [None]}, TypeError),
    ({"rates": [4.1, 4.2]}, TypeError),
    ({"rates": ["4.1", "4.2"]}, TypeError),

    # 5. Items are dicts, but 'mid' is missing/wrong
    ({"rates": [{"ask": 4.1}]}, KeyError),  # Missing 'mid'
    ({"rates": [{"MID": 4.1}]}, KeyError),  # Case sensitive failure
    ({"rates": [{}]}, KeyError),  # Empty dict
]


@pytest.mark.parametrize("payload, expected_exception", FATAL_JSON_PAYLOADS)
@patch("api.requests.get")
def test_json_schema_fatal_crashes(mock_get, payload, expected_exception):
    """Testing how the code handles fundamentally broken JSON structures."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = payload

    # The current api.py will violently crash with native Python errors here,
    # because it lacks basic dictionary/list validation.
    with pytest.raises(expected_exception):
        fetch_currency_data("USD", 1)


# =====================================================================
# BLOCK 5: SILENT DATA POISONING (5 Tests)
# These tests represent the MOST DANGEROUS bugs. The code doesn't crash,
# but it leaks garbage data (strings, lists, booleans) into the financial calculations.
# =====================================================================

SILENT_POISON_PAYLOADS = [
    {"rates": [{"mid": "4.15"}]},  # String leak
    {"rates": [{"mid": None}]},  # NoneType leak
    {"rates": [{"mid": True}]},  # Boolean leak
    {"rates": [{"mid": [4.15]}]},  # List leak
    {"rates": [{"mid": {"val": 4.1}}]},  # Dict leak
]


@pytest.mark.parametrize("payload", SILENT_POISON_PAYLOADS)
@patch("api.requests.get")
def test_json_silent_data_poisoning(mock_get, payload):
    """Testing if the API module allows non-float garbage data to pass through."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = payload

    data = fetch_currency_data("USD", 1)

    # If the data array contains anything that isn't a strict float, the test passes
    # (meaning we successfully proved the code is vulnerable to poisoning).
    is_poisoned = not isinstance(data[0], float) or isinstance(data[0], bool)
    assert is_poisoned, "The application failed to sanitize incoming data types."


# =====================================================================
# BLOCK 6: BOUNDARY CONDITIONS & LIMITS (5 Tests)
# =====================================================================

@patch("api.requests.get")
def test_api_boundary_255_days(mock_get):
    """Valid business case: Exactly on the NBP limit."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"rates": [{"mid": 4.0}] * 255}
    data = fetch_currency_data("USD", 254)  # count becomes 255
    assert len(data) == 255


@patch("api.requests.get")
def test_api_boundary_256_days_rejection(mock_get):
    """Boundary violation: Over the NBP limit."""
    mock_get.return_value.status_code = 400
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
    with pytest.raises(Exception, match="API Error"):
        fetch_currency_data("USD", 255)  # count becomes 256


@patch("api.requests.get")
def test_api_zero_sessions(mock_get):
    """Edge case: 0 sessions requested."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"rates": [{"mid": 4.0}]}
    data = fetch_currency_data("USD", 0)  # count becomes 1
    assert len(data) == 1


@patch("api.requests.get")
def test_api_html_response_crash(mock_get):
    """Server sends an HTML error page (e.g. 503 Service Unavailable proxy page)."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200  # Proxies sometimes return 200 for error pages
    mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "<html>", 0)

    # In requests > 2.27.0, JSONDecodeError inherits from RequestException.
    # We expect the custom wrapper to catch it.
    with pytest.raises(Exception, match="API Error fetching data"):
        fetch_currency_data("USD", 5)


@patch("api.requests.get")
def test_api_empty_valid_array(mock_get):
    """Valid edge case: JSON is perfect, but array is empty."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"rates": []}
    assert fetch_currency_data("USD", 5) == []