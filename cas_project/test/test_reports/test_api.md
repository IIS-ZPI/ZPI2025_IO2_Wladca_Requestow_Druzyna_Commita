# Application Test Report No. 08 (API Hardening & Fuzz Testing)
**Date**: 2026-04-30

## A. Description of performed activities.

**Environments and devices on which the tests were conducted:**
1. Ubuntu 22.04 LTS / Bash Terminal
2. Mocked API Endpoint Environment (Pytest with `unittest.mock.patch`)

**Tester's login and password:** Automated Pytest Suite
**Build number**: 2.1.3          **dated**: 2026-04-30

### Application areas and types of tests performed:
| Application area | Types of tests performed | Time spent on tests |
| :--- | :--- | :--- |
| **API Pre-Flight Validation (`api.py`)** | Input mutilation testing (injecting None, Strings, Lists into numerical parameters before HTTP request generation). | 1.0h |
| **Network Resilience (`api.py`)** | Simulation of deep socket failures, proxy errors, SSL failures, and obscure HTTP status codes (e.g., 418, 429, 502). | 1.0h |
| **JSON Schema Poisoning (`api.py`)** | Parametrized Fuzz Testing injecting 20+ malformed JSON structures (missing keys, altered types, empty dictionaries) to test structural fragility. | 1.5h |

---

## B. Summary of all defects.

**Identified Systemic Vulnerabilities:**
a) **List Comprehension Crash Vulnerability:** The core data extraction mechanism (`[item['mid'] for item in data['rates']]`) is highly volatile. It inherently assumes the response is a dictionary containing a list of dictionaries. Providing an integer, a string, or a missing key causes fatal native Python crashes (`TypeError`, `KeyError`) rather than returning a controlled error.
b) **Parameter Type Blindness:** The `sessions` variable is concatenated directly into the URL path (`count = sessions + 1`). Passing strings, lists, or `None` breaks the application locally before the HTTP request is even dispatched.
c) **Data Type Leakage (Silent Failure):** If the JSON structure is perfectly maintained (keys exist), but the `mid` value is replaced with a String, Boolean, or nested Dictionary, `api.py` extracts it without triggering any errors. This corrupts the downstream data pipeline, guaranteeing a crash in the analytical/mathematical modules later.

---

## C. Detailed description of defects

### Test 8a (Pre-Flight Input Fuzzing)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 08
**Priority:** High
**Location of the problem:** `cas_project/api.py` -> `count = sessions + 1`

**Steps to reproduce:**
1. Call the function with an invalid data type for the `sessions` parameter (e.g., `fetch_currency_data("USD", "5")` or `fetch_currency_data("USD", [5])`).

**Test result:** The system immediately crashes with a `TypeError` (e.g., "can only concatenate str (not 'int') to str"). The module lacks basic input sanitization and `isinstance()` checks before attempting mathematical or string operations.

### Test 8b (JSON Schema Fatal Crashes)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 08
**Priority:** Critical
**Repeatability:** 100% when NBP API schema deviates.
**Location of the problem:** `cas_project/api.py` -> Data extraction block

**Steps to reproduce:**
1. The external API returns an HTTP 200 OK.
2. The payload is iteratively replaced with malformed variations (e.g., `{"rates": [1, 2, 3]}`, `{"table": "A"}`, `{"rates": [{"mId": 4.1}]}`).

**Test result:** The custom `requests.exceptions.RequestException` block only protects network failures. Because the JSON payload is structurally broken, the attempt to parse it throws unhandled, native `KeyError` or `TypeError` exceptions, terminating the entire application workflow.

### Test 8c (Silent Data Poisoning)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 08
**Priority:** Critical
**Location of the problem:** `cas_project/api.py` -> `return [item['mid']...`

**Steps to reproduce:**
1. The external API returns an HTTP 200 OK.
2. The payload contains valid keys, but corrupted data types (e.g., `{"rates": [{"mid": "4.15"}]}`).

**Test result:** The module successfully returns `["4.15"]`. While `api.py` does not crash, it fails to guarantee the integrity of the data contract. It leaks non-float types into the application, which will silently poison subsequent mathematical calculations.

---

## D. Summary of exit criteria for all tests.
1. **Did we manage to perform the planned tests?** Yes. 45 aggressive, fuzzer-style tests were executed against the API module. 44 passed (successfully triggering the expected failures/crashes), proving the module is highly vulnerable to unexpected data.
2. **Risks that materialized:** The `api.py` script acts as an unprotected data pipe. By trusting external API structures and user inputs implicitly, it exposes the internal application to fatal crashes based on third-party schema changes.
3. **Conclusions for the future (Remediation Plan):** 
    *   **Input Guards:** Enforce strict type checking (`isinstance(sessions, int)`) at the top of the function.
    *   **Schema Validation:** The code must verify the JSON structure before parsing: `isinstance(data, dict)`, `'rates' in data`, and `isinstance(data['rates'], list)`.
    *   **Type Assertions:** Loop through the items safely using `.get('mid')` and strictly verify `isinstance(val, (int, float))` to prevent data poisoning.