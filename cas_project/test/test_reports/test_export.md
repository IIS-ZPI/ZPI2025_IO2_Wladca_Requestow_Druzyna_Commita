# Application Test Report No. 11 (Export Parameter & I/O Vulnerabilities)
**Date**: 2024-06-05

## A. Description of performed activities.

**Environments and devices on which the tests were conducted:**
1. Ubuntu 22.04 LTS / Bash Terminal
2. Pytest Automated Test Runner

**Tester's login and password:** Automated Pytest Suite
**Build number**: 2.2.3          **dated**: 2024-06-05

### Application areas and types of tests performed:
| Application area | Types of tests performed | Time spent on tests |
| :--- | :--- | :--- |
| **OS Exception Handling (`export.py`)** | Simulating OS-level file write rejections (`PermissionError`). | 0.5h |
| **Type Coercion & File Descriptors (`export.py`)** | Fuzzing the `filename` parameter to test for unexpected Python type coercion (Booleans and Integers acting as File Descriptors). | 1.0h |

---

## B. Summary of all defects.

**Identified Systemic Vulnerabilities:**
a) **Dangerous Type Coercion (Stdout Leak):** The `export_to_csv` function accepts a `filename` parameter but does not verify if it is actually a string. If a Boolean (`True`) is passed, Python evaluates it as `1`. File descriptor `1` represents `stdout`. The application blindly writes the CSV output directly to the console instead of throwing an error or saving a file.
b) **File Descriptor Crash:** Passing a random integer (e.g., `1234`) bypassing string validation causes the `open()` function to attempt to hook into a low-level OS file descriptor[cite: 12]. This causes a hard crash (`OSError: Bad file descriptor`) rather than a controlled type validation error.
c) **Unmanaged OS Interruptions (Hard Crash):** The file export module executes `with open(...)` completely unprotected[cite: 12]. If the OS denies access (e.g., restricted folders), the application suffers a fatal `PermissionError`, terminating the program and resulting in the loss of in-memory data.

---

## C. Detailed description of defects

### Test 11a (The File Descriptor Bypass)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 11
**Priority:** Medium
**Location of the problem:** `cas_project/export.py` -> `with open(filename...`

**Steps to reproduce:**
1. Call `export_to_csv(data, 1234)`.
2. The function passes the integer directly into the `open()` context manager[cite: 12].

**Test result:** The system crashes with `OSError: [Errno 9] Bad file descriptor`. The test expected a `TypeError` due to bad input, but the lack of type guards allowed the payload to reach the OS-level file handler, resulting in an unhandled native crash.

### Test 11b (The `stdout` Boolean Leak)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 11
**Priority:** High
**Location of the problem:** `cas_project/export.py` -> `with open(filename...`

**Steps to reproduce:**
1. Call `export_to_csv(data, True)`.

**Test result:** The test failed because the application *did not crash*. Instead, Python coerced `True` into `1`, and the CSV module successfully wrote the data into the application's standard output stream, followed by a misleading success message: `Success: Data successfully exported to True.`

### Test 11c (The Guaranteed I/O Failure)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 11
**Priority:** Critical (Data Loss)
**Location of the problem:** `cas_project/export.py` -> `with open(filename...`

**Steps to reproduce:**
1. A valid dataset is passed, but the system denies write access (simulated `PermissionError`).

**Test result:** The application crashed violently. It failed to catch the OS error internally, meaning it cannot gracefully inform the user to select a different save directory. 

---

## D. Summary of exit criteria for all tests.
1. **Did we manage to perform the planned tests?** Yes. Out of 28 tests, the 3 failures successfully exposed critical blind spots in how Python handles file I/O types.
2. **Risks that materialized:** Standard Python functions like `open()` have deeply embedded legacy behaviors (like integer-to-file-descriptor routing). Trusting user input or upstream functions to provide valid strings without explicit runtime checks is highly dangerous.
3. **Conclusions for the future (Remediation Plan):** 
    *   **Type Guarding:** The `export.py` module must add a strict check at the top of the function: `if not isinstance(filename, str): raise TypeError("Filename must be a string")`. This prevents Booleans and Integers from reaching the file handler.
    *   **I/O Wrapping:** The core operation (`with open(...)`)[cite: 12] MUST be wrapped inside a `try...except (OSError, IOError, PermissionError)` block to prevent total application failure upon OS rejection.