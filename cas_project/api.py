import requests

BASE_URL = "http://api.nbp.pl/api/exchangerates/rates/A"


class DataParsingError(Exception):
    """Raised when the NBP API response cannot be validated or parsed."""


def _validate_rates_payload(data) -> list:
    if not isinstance(data, dict):
        raise DataParsingError("JSON response must be an object")
    if "rates" not in data:
        raise DataParsingError("Missing 'rates' in JSON response")
    rates = data["rates"]
    if not isinstance(rates, list):
        raise DataParsingError("'rates' must be a list")
    for index, item in enumerate(rates):
        if not isinstance(item, dict):
            raise DataParsingError(f"Rate item at index {index} must be an object")
        if "mid" not in item:
            raise DataParsingError(f"Missing 'mid' in rate item at index {index}")
    return rates


def _extract_mid_floats(rates: list) -> list[float]:
    values = []
    for index, item in enumerate(rates):
        mid = item["mid"]
        if isinstance(mid, bool) or mid is None:
            raise DataParsingError(f"Invalid 'mid' value at index {index}")
        if not isinstance(mid, (int, float)):
            raise DataParsingError(f"'mid' must be numeric at index {index}")
        values.append(float(mid))
    return values


def fetch_currency_data(currency: str, sessions: int) -> list:
    """
    Fetches currency data from the NBP API.
    We fetch `sessions + 1` to be able to calculate changes for the specified period.
    NBP API allows topCount queries up to 255, which represents roughly 1 calendar year of business days.
    """
    if not isinstance(currency, str):
         raise TypeError("currency must be a string")
    if not isinstance(sessions, int) or isinstance(sessions, bool):
         raise TypeError("sessions must be an integer")
    if sessions < 0:
         raise ValueError("sessions must be a non-negative integer")

    count = sessions + 1
    url = f"{BASE_URL}/{currency}/last/{count}/?format=json"
    
    try:
         response = requests.get(url, timeout=10)
         if response.status_code == 404:
             return []
         response.raise_for_status()
         data = response.json()
         rates = _validate_rates_payload(data)
         return _extract_mid_floats(rates)
    except requests.exceptions.RequestException as e:
         raise Exception(f"API Error fetching data for {currency}: {str(e)}")
