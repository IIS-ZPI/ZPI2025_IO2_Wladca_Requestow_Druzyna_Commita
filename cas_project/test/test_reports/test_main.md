# Application Test Report No. 15 (Integration & Edge-Case Orchestration)
**Date**: 2026-04-30

## A. Description of Activities

**Environments and devices on which the tests were conducted:**
1. System Ubuntu 22.04 LTS / Bash Terminal
2. Pytest Automated Test Runner with Mocked `stdin`

**Tester's login and password:** Automated Pytest Suite
**Build number**: 2.3.1          **dated**: 2026-04-30

### Application areas and types of tests performed:
| Application area | Types of tests performed | Time spent on tests |
| :--- | :--- | :--- |
| **User Interface (CLI) Orchestration** | End-to-end integration testing of `main.py` using mocked user input streams. | 1.0h |
| **Edge-Case Logic & Stability** | Negative testing focused on malformed currency pairs and resource optimization. | 1.0h |

---

## B. Summary of all defects

**Identified Systemic Vulnerabilities:**
a) **Unsafe String Unpacking (Double-Slash Crash):** The logic responsible for splitting currency pairs validates the presence of a separator but not its quantity. Providing a pair with multiple slashes (e.g., `EUR//USD`) results in an unhandled `ValueError` because the code expects exactly two values from the split operation.
b) **Inefficient API Resource Management:** During currency pair analysis, the application initiates network requests for both currencies sequentially without verifying the success of the first call. This leads to redundant API traffic when the first currency in a pair is invalid.

---

## C. Detailed description of defects

### Test 15a (The Double-Slash Crash)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 15
**Priority:** Critical (Fatal Application Crash)
**Location of the problem:** `cas_project/main.py` -> `c1, c2 = pair.split("/")`

**Steps to reproduce:**
1. Navigate to Option 3 (Distribution of Changes).
2. Enter a currency pair with two slashes (e.g., `EUR//USD`).

**Test result:** The application crashes immediately with `ValueError: too many values to unpack (expected 2)`. This exposes a lack of input validation before variable assignment, causing the entire process to terminate.

### Test 15b (Redundant Network Execution)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 15
**Priority:** Medium (Performance/Efficiency)
**Location of the problem:** `cas_project/main.py` -> Option 3 Logic

**Steps to reproduce:**
1. Enter a valid format pair where the first currency is invalid (e.g., `INVALID/USD`).

**Test result:** The system continues to fetch data for the second currency (`USD`) even after the first call has already failed. This results in a `call_count` of 2 for the API fetcher, proving the lack of short-circuit logic in the orchestration flow.

---

## D. Summary of exit criteria for all tests
1. **Did we manage to perform the planned tests?** Yes. 18 automated integration tests were executed.
2. **Risks that materialized:** User input errors in complex modes (Option 3) bypass simple checks and lead to native Python exceptions that crash the interface.
3. **Conclusions for the future (Remediation Plan):** 
    * **Harden Unpacking:** Verify the list length from `split("/")` before unpacking into `c1, c2`.
    * **API Guards:** Only call the second API fetch if the first one returns valid data.
    * **Global Exception Handling:** While the `try...except` block exists, it failed to prevent the unpacking crash because the error occurred outside the protected block.