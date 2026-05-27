import statistics
import math


def _is_finite_number(value) -> bool:
    """
    Returns True only for finite int/float values.
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _filter_finite_values(values: list) -> list:
    """
    Filters out non-finite numeric values (NaN, +/-Inf) and non-numeric entries.
    """
    return [value for value in values if _is_finite_number(value)]

def session_analysis(rates: list) -> tuple:
    """
    Calculates the number of rising, falling, and unchanged sessions.
    """
    cleaned_rates = _filter_finite_values(rates)

    if len(cleaned_rates) < 2:
        return 0, 0, 0
    
    rises, falls, unchanged = 0, 0, 0
    # Start loop from index 1 and compare to index 0
    for i in range(1, len(cleaned_rates)):
        if cleaned_rates[i] > cleaned_rates[i-1]:
            rises += 1
        elif cleaned_rates[i] < cleaned_rates[i-1]:
             falls += 1
        else:
             unchanged += 1
             
    return rises, falls, unchanged

def statistical_measures(rates: list) -> dict:
    """
    Calculates median, mode, sample standard deviation, and coefficient of variation.
    The calculations are done on the actual fetched periods.
    """
    # Exclude the first "extra" element we grabbed for difference calculations
    # to maintain strict exact period calculations
    target_rates = rates[1:] if len(rates) > 1 else rates
    target_rates = _filter_finite_values(target_rates)
    
    if not target_rates:
         return {}
         
    n = len(target_rates)
    median = statistics.median(target_rates)
    
    try:
         mode = statistics.mode(target_rates)
    except statistics.StatisticsError:
         mode = target_rates[0] # Fallback in case of multi-modal
         
    if n > 1:
         std_dev = statistics.stdev(target_rates)
         mean_val = statistics.mean(target_rates)
         coef_var = (std_dev / mean_val) if mean_val != 0 else 0
    else:
         std_dev, coef_var = 0.0, 0.0
         
    return {
         "median": round(median, 4),
         "mode": round(mode, 4),
         "standard_deviation": round(std_dev, 4),
         "coefficient_of_variation": round(coef_var, 4)
    }

def distribution_of_changes(rates1: list, rates2: list) -> list:
    """
    Calculates distribution of cross-rate changes, splitting into 13 equal intervals.
    """
    n = min(len(rates1), len(rates2))
    cross_rates = []
    for i in range(n):
        first = rates1[i]
        second = rates2[i]
        if not (_is_finite_number(first) and _is_finite_number(second)):
            continue
        if second == 0:
            continue
        cross_rates.append(first / second)
    
    changes = []
    for i in range(1, len(cross_rates)):
        changes.append(cross_rates[i] - cross_rates[i-1])
        
    if not changes: return []
    
    bucket_count = 13
    min_c = min(changes)
    max_c = max(changes)
    span = max_c - min_c

    # Guard against floating-point jitter when changes are almost identical.
    magnitude = max(abs(min_c), abs(max_c), 1.0)
    jitter_tolerance = max(1e-12 * magnitude, 1e-15)
    if span <= jitter_tolerance:
        lower_bound = min_c - jitter_tolerance / 2
        upper_bound = max_c + jitter_tolerance / 2
    else:
        lower_bound = min_c
        upper_bound = max_c

    interval_size = (upper_bound - lower_bound) / bucket_count
         
    ranges = []
    for i in range(bucket_count):
         start_val = lower_bound + i * interval_size
         end_val = start_val + interval_size
         ranges.append({"start": start_val, "end": end_val, "count": 0})
         
    for c in changes:
         bucket_index = int((c - lower_bound) / interval_size)
         if bucket_index < 0:
             bucket_index = 0
         elif bucket_index >= bucket_count:
             bucket_index = bucket_count - 1
         ranges[bucket_index]["count"] += 1
                 
    return ranges
