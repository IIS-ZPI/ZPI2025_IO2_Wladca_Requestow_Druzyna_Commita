# Application Test Report No. 05 (Destructive & Edge-Case Testing)
**Date**: 2024-06-02

## A. Description of performed activities.

**Environments and devices on which the tests were conducted:**
1. Ubuntu 22.04 LTS / Bash Terminal
2. GitHub Actions CI Environment (Automated Runner)

**Tester's login and password:** Automated Pytest Suite / No authorization
**Build number**: 2.1.1-rc1          **dated**: 2024-06-02

### Application areas and types of tests performed:
| Application area | Types of tests performed | Time spent on tests |
| :--- | :--- | :--- |
| **Session Analysis (`analysis.py`)** | Destructive testing, logical bug hunting, `NaN` (Not a Number) and `Infinity` data injection, float precision boundary testing. | 1.5h |
| **Statistical Measures (`analysis.py`)** | Mathematical overflow simulation (`1e250`), bimodal distribution edge cases, zero-mean division checks. | 1.5h |
| **Distribution of Changes (`analysis.py`)** | Micro-interval float leak checks, zero-base currency simulation, unmatched list dimensions. | 1h |

---

## B. Summary of all defects.
**1) Fixed and retested:**
a) None (This is the initial execution report of the destructive test suite).

**2) To do / Identified Vulnerabilities:**
a) The application silently absorbs `NaN` values, corrupting the business logic in `session_analysis`.
b) The `statistics.stdev` function crashes the application with an `AttributeError` when exposed to poisoned data (`NaN`).
c) The application fails to throw an `OverflowError` during massive variance calculations, returning an unhandled `inf` (Infinity) instead.
d) The histogram generation creates corrupted `NaN` boundaries if cross-rate mathematical operations fail.

**3) Those that are risky to fix at the moment:**
a) Implementing strict type-checking and float-sanitization globally across the `analysis.py` module may require extensive regression testing to ensure standard inputs are not accidentally blocked.

---

## C. Detailed description of defects

### Test 5a (Silent Logic Bug)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 05
**Priority:** High
**Repeatability:** 100% when API data is corrupted.
**Environment:** Python 3.12 Backend
**Location of the problem:** `cas_project/analysis.py` -> `session_analysis()`

**Steps to reproduce:**
1. Simulate an API failure where one of the daily rates is missing, resulting in `math.nan`.
2. Pass the list `[4.1, math.nan, 4.2]` to the function.
3. The application processes the data without crashing.

**Test result:** The system falsely categorizes the `NaN` transition as an "unchanged" session. Because Python evaluates `math.nan > float` as `False` and `math.nan < float` as `False`, the code falls through to the `else` block, silently corrupting the final analytical output.

### Test 5b (Statistics Library Crash)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 05
**Priority:** Critical
**Repeatability:** 100% 
**Location of the problem:** `cas_project/analysis.py` -> `statistical_measures()`

**Steps to reproduce:**
1. Pass a list containing a `NaN` value (e.g., `[4.1, 4.2, math.nan, 4.4]`) to the statistical analyzer.
2. The function passes the raw list directly to Python's standard `statistics.stdev()` method.

**Test result:** Crash. `AttributeError: 'float' object has no attribute 'numerator'`. The internal fractions engine of the standard library cannot process `NaN`, immediately terminating the application.

### Test 5c (Variance Overflow Handling)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 05
**Priority:** Medium
**Repeatability:** 100% for extreme values.
**Location of the problem:** `cas_project/analysis.py` -> `statistical_measures()`

**Steps to reproduce:**
1. Inject astronomically large floats into the dataset (e.g., `1e250`, `-1e250`).
2. Execute the function.

**Test result:** The test expected the application to gracefully raise an `OverflowError` to be handled by the UI. Instead, the calculation exceeds Python's maximum float size, silently converting the standard deviation to `Infinity` (`inf`), which is then passed down the pipeline.

### Test 5d (Histogram Boundary Corruption)
**Who detected:** Automated Pytest Suite
**Report in which detected:** no. 05
**Priority:** High
**Repeatability:** 100% when input lists contain `NaN`.
**Location of the problem:** `cas_project/analysis.py` -> `distribution_of_changes()`

**Steps to reproduce:**
1. Provide a base currency array containing `0.0`, or pre-poisoned `NaN` values.
2. The `min()` and `max()` functions attempt to evaluate the corrupted cross-rates.

**Test result:** The interval size variable (`interval_size`) evaluates to `NaN`. Subsequently, every generated bucket boundary (`start` and `end`) evaluates to `NaN`, completely destroying the UI formatting for the histogram.

---

## D. Summary of exit criteria for all tests.
1. **Did we manage to perform the planned tests?** Yes. 25 highly destructive edge-case tests were executed. 21 passed (proving strong baseline stability), while 4 critical vulnerabilities were exposed.
2. **Were there any difficulties?** Identifying the exact C-level behaviors of Python's math libraries when handling non-finite floats required deep inspection.
3. **Verification of work time estimates.** The testing phase required slightly more time than standard UAT (4 hours) due to the necessity of designing mathematical anomalies that bypass standard error handlers.
4. **Risks that materialized:** Standard Python math libraries (`statistics`, `min`, `max`) are not inherently safe against poisoned data streams (`NaN`/`Infinity`). Relying on them without pre-validation is a security/stability risk.
5. **Conclusions for the future:** The `analysis.py` module must implement a strict data sanitization layer. Before passing any lists to iterative loops or statistical modules, the application must aggressively filter out or reject `math.nan` and `math.inf` types to prevent silent logic failures.