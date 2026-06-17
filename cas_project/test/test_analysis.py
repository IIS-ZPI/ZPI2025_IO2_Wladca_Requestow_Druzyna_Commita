import pytest
import math
import statistics
from analysis import session_analysis, statistical_measures, distribution_of_changes

# =====================================================================
# PART 1: DESTRUCTIVE TESTS FOR session_analysis
# =====================================================================

def test_sa_with_strings():
    """CRASH: Fails due to comparing string with float."""
    rates = [4.1, 4.2, "4.3", 4.4]
    with pytest.raises(TypeError):
        session_analysis(rates)

def test_sa_with_nan_silent_logic_bug():
    """
    LOGICAL BUG: math.nan > float is False, math.nan < float is False.
    The current code will silently count NaN transitions as 'unchanged'!
    """
    rates = [4.1, math.nan, 4.2]
    rises, falls, unchanged = session_analysis(rates)
    # The current code will wrongly return unchanged=1. We assert the expected correct business logic (it should probably raise an error or ignore).
    # This assertion will FAIL on the current code, proving the bug.
    assert unchanged == 0, "Code incorrectly categorized NaN as 'unchanged'!"

def test_sa_with_infinity():
    """Checking behavior with math.inf (e.g., hyperinflation data anomaly)."""
    rates = [4.1, math.inf, 4.2]
    rises, falls, unchanged = session_analysis(rates)
    assert rises == 1
    assert falls == 0
    assert unchanged == 0

def test_sa_micro_float_differences():
    """LOGICAL BUG: Tests if extremely small float changes are detected."""
    rates = [4.100000000000000, 4.100000000000001]
    rises, falls, unchanged = session_analysis(rates)
    assert rises == 1

def test_sa_negative_rates():
    """Business logic anomaly: exchange rates shouldn't be negative, but math works."""
    rates = [-4.1, -4.2, -4.0]
    rises, falls, unchanged = session_analysis(rates)
    assert rises == 1  # -4.2 to -4.0
    assert falls == 1  # -4.1 to -4.2

def test_sa_boolean_injection():
    """
    LOGICAL BUG: Python treats True as 1.0 and False as 0.0.
    The function will silently process this garbage data.
    """
    rates = [True, False, True]
    rises, falls, unchanged = session_analysis(rates)
    assert falls == 1 # True to False
    assert rises == 1 # False to True

def test_sa_generator_instead_of_list():
    """CRASH: The function expects a list (uses len() and indexing), passing a generator breaks it."""
    rates_gen = (x for x in [4.1, 4.2, 4.3])
    with pytest.raises(TypeError):
        session_analysis(rates_gen)

def test_sa_all_identical_large_dataset():
    """Performance & logic check for completely flat data."""
    rates = [3.14] * 50000
    rises, falls, unchanged = session_analysis(rates)
    assert unchanged == 49999

# =====================================================================
# PART 2: DESTRUCTIVE TESTS FOR statistical_measures
# =====================================================================

def test_sm_with_nan_contamination():
    """
    LOGICAL BUG: NaN poisons standard statistics functions.
    Mean/Stdev will become NaN, and round() might behave unexpectedly.
    """
    rates = [4.1, 4.2, math.nan, 4.4] # 4.1 is ignored by rates[1:]
    stats = statistical_measures(rates)
    assert not math.isnan(stats["standard_deviation"]), "NaN leaked into final statistical output!"

def test_sm_almost_zero_mean():
    """
    CRASH / LOGICAL BUG: Mean is infinitesimally small (e.g., 1e-16), bypassing `if mean_val != 0`,
    but dividing by it causes an astronomical coefficient of variation.
    """
    rates = [100.0, 1e-16, -1e-16] # 100.0 is dropped
    stats = statistical_measures(rates)
    assert stats["coefficient_of_variation"] < 1e100, "Coefficient of variation exploded due to near-zero mean!"

def test_sm_overflow_variance():
    """CRASH: extremely large numbers can cause OverflowError in stdev calculation."""
    rates = [1.0, 1e250, -1e250] # 1.0 is dropped
    with pytest.raises(OverflowError):
         statistical_measures(rates)

def test_sm_exact_same_elements():
    """Checks fallback logic when standard deviation is exactly 0."""
    rates = [1.0, 5.0, 5.0, 5.0] # 1.0 dropped
    stats = statistical_measures(rates)
    assert stats["standard_deviation"] == 0.0
    assert stats["coefficient_of_variation"] == 0.0

def test_sm_bimodal_distribution():
    """Checks the custom fallback for mode when two values have the exact same frequency."""
    rates = [1.0, 2.0, 2.0, 3.0, 3.0] # 1.0 dropped
    stats = statistical_measures(rates)
    # Depending on Python version, statistics.mode either returns the first common or raises Error.
    # The code handles StatisticsError by returning target_rates[0].
    assert stats["mode"] in [2.0, 3.0]

def test_sm_single_valid_element_after_slice():
    """Edge case: len(rates) == 2, so target_rates has exactly 1 element."""
    rates = [4.0, 5.0]
    stats = statistical_measures(rates)
    assert stats["standard_deviation"] == 0.0
    assert stats["median"] == 5.0

def test_sm_two_elements_zero_mean():
    """Checks division by exact zero."""
    rates = [99.0, 5.0, -5.0]
    stats = statistical_measures(rates)
    assert stats["coefficient_of_variation"] == 0.0

def test_sm_string_contamination():
    """CRASH: statistics module cannot process strings."""
    rates = [1.0, 2.0, "3.0"]
    with pytest.raises(TypeError):
        statistical_measures(rates)

# =====================================================================
# PART 3: DESTRUCTIVE TESTS FOR distribution_of_changes
# =====================================================================

def test_doc_divide_by_zero_in_base_currency():
    """CRASH: rates2 contains 0, causing ZeroDivisionError during cross_rates generation."""
    ranges = distribution_of_changes([4.0, 4.0, 4.0], [1.0, 0.0, 1.0])
    assert len(ranges) == 13
    assert sum(r["count"] for r in ranges) == 1

def test_doc_empty_rates1():
    """Checks how it handles completely empty input for the primary currency."""
    assert distribution_of_changes([], [1.0, 2.0]) == []

def test_doc_different_list_sizes_extreme():
    """Logic check: relies on n = min(len(rates1), len(rates2)). Does it correctly drop the excess?"""
    ranges = distribution_of_changes([4.0, 4.1], [1.0] * 1000)
    assert len(ranges) == 13
    total_count = sum(r['count'] for r in ranges)
    assert total_count == 1 # Only 2 cross rates = 1 change

def test_doc_interval_fallback_bug():
    """
    LOGICAL BUG: If max_c == min_c, interval_size becomes 0.0001.
    If the changes are massive (e.g., 1,000,000), buckets will go from
    1,000,000 to 1,000,000.0013. Float jitter might cause counts to drop!
    """
    massive_val = 1000000.0
    rates1 = [massive_val, massive_val * 2, massive_val * 3]
    rates2 = [1.0, 1.0, 1.0]
    # The change is exactly 1,000,000 each time.
    ranges = distribution_of_changes(rates1, rates2)
    total_count = sum(r['count'] for r in ranges)
    assert total_count == 2, "Fallback logic caused data to fall outside the 13 buckets!"

def test_doc_nan_in_cross_rates():
    """CRASH / LOGICAL BUG: min() and max() functions fail predictably if changes contain NaN."""
    rates1 = [4.0, math.nan, 4.2]
    rates2 = [1.0, 1.0, 1.0]
    # NaN propagates to `changes`. min(changes) might return NaN.
    # interval_size becomes NaN. Loop ranges become NaN.
    # This will silently create garbage buckets or crash.
    ranges = distribution_of_changes(rates1, rates2)
    assert not math.isnan(ranges[0]["start"]), "Histogram generated NaN boundaries!"

def test_doc_infinity_in_cross_rates():
    """CRASH: interval_size will become Inf, crashing the loop."""
    rates1 = [4.0, math.inf, 4.2]
    rates2 = [1.0, 1.0, 1.0]
    ranges = distribution_of_changes(rates1, rates2)
    assert ranges[0]["start"] != math.inf, "Histogram failed to handle Infinity!"

def test_doc_boundary_condition_floating_point():
    """
    LOGICAL BUG: Testing if a value exactly on the boundary of an internal bucket (not the 12th)
    is assigned properly or skipped due to float < vs <= operators.
    """
    rates1 = [1.0, 1.5, 2.0] # Change is exactly 0.5. Min=0.5, Max=0.5
    rates2 = [1.0, 1.0, 1.0]
    ranges = distribution_of_changes(rates1, rates2)
    total_count = sum(r['count'] for r in ranges)
    assert total_count == 2

def test_doc_negative_base_currency():
    """Checking math stability if the base currency is negative (invalid business case)."""
    ranges = distribution_of_changes([4.0, 4.2, 4.4], [-1.0, -1.0, -1.0])
    total_count = sum(r['count'] for r in ranges)
    assert total_count == 2

def test_doc_micro_interval_precision():
    """
    LOGICAL BUG: Very small float differences in `changes`.
    Checks if `c < r["end"]` correctly catches numbers like 0.000000000000001.
    """
    rates1 = [1.0, 1.000000000000001, 1.000000000000002]
    rates2 = [1.0, 1.0, 1.0]
    ranges = distribution_of_changes(rates1, rates2)
    total_count = sum(r['count'] for r in ranges)
    assert total_count == 2, "Lost micro-float values due to precision errors!"