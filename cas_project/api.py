import requests
import math

BASE_URL = "http://api.nbp.pl/api/exchangerates/rates/A"

def fetch_currency_data(currency: str, sessions: int) -> list:
    """
    Fetches currency data from the NBP API.
    Includes strict pre-flight input validation and JSON sanitization.
    """
    # 1. Pre-flight Validation (Defense against input fuzzing)
    if not isinstance(currency, str):
        raise TypeError("Currency must be a string")
    if not currency.isalpha() or len(currency) > 3:
        raise Exception("Invalid currency code")
    if type(sessions) is not int:  # Strict type check (blocks boolean)
        raise TypeError("Sessions must be an integer")
    if sessions < 0:
        raise Exception("Sessions cannot be negative")
        
    count = sessions + 1
    url = f"{BASE_URL}/{currency}/last/{count}/?format=json"
    
    try:
         response = requests.get(url, timeout=10)
         if response.status_code == 404:
             return []
         response.raise_for_status()
         data = response.json()
         
         # 2. JSON Schema & Poisoning Validation
         # SEPARATED TYPE AND KEY VALIDATION
         if not isinstance(data, dict):
             raise TypeError("Malformed JSON: response is not a dictionary")
         if 'rates' not in data:
             raise KeyError("Malformed JSON: missing 'rates' array")
         if not isinstance(data['rates'], list):
             raise TypeError("Malformed JSON: 'rates' is not a list")
             
         clean_rates = []
         for item in data['rates']:
             # Separate validation for the object and the key inside the list
             if not isinstance(item, dict):
                 raise TypeError("Malformed JSON: rate item is not a dictionary")
             if 'mid' not in item:
                 raise KeyError("Malformed JSON: missing 'mid' in rate item")
                 
             mid = item['mid']
             
             # 3. Protection against 'Silent Data Poisoning'
             # Instead of silently ignoring invalid data, it is safer to raise an exception
             if type(mid) not in (int, float) or type(mid) is bool:
                 raise TypeError("Malformed JSON: 'mid' must be a valid number")
                 
             clean_rates.append(float(mid))
             
         return clean_rates
         
    except requests.exceptions.RequestException as e:
         raise Exception(f"API Error fetching data for {currency}: {str(e)}")
    except ValueError as e:
         # Catching HTML decoded as JSON errors
         raise Exception(f"API Error fetching data for {currency}: Invalid JSON response")