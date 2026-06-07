import math
import statistics

def session_analysis(rates: list) -> tuple:
    """
    Calculates the number of rising, falling, and unchanged sessions.
    """
    if not isinstance(rates, list):
        raise TypeError("rates must be a list")
    if len(rates) < 2:
        return 0, 0, 0

    rises, falls, unchanged = 0, 0, 0
    # Start loop from index 1 and compare to index 0
    for i in range(1, len(rates)):
        prev = rates[i-1]
        curr = rates[i]

        if not isinstance(prev, (int, float)) or not isinstance(curr, (int, float)):
            raise TypeError("rates values must be numeric")
        if math.isnan(prev) or math.isnan(curr):
            continue

        if curr > prev:
            rises += 1
        elif curr < prev:
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

    if not target_rates:
         return {}

    if any(not isinstance(x, (int, float)) for x in target_rates):
         raise TypeError("rates values must be numeric")

    valid_rates = [float(x) for x in target_rates if math.isfinite(x)]
    if not valid_rates:
         return {
             "median": 0.0,
             "mode": 0.0,
             "standard_deviation": 0.0,
             "coefficient_of_variation": 0.0
         }

    n = len(valid_rates)
    median = statistics.median(valid_rates)

    try:
         mode = statistics.mode(valid_rates)
    except statistics.StatisticsError:
         mode = valid_rates[0] # Fallback in case of multi-modal

    if n > 1:
         std_dev = statistics.stdev(valid_rates)
         if not math.isfinite(std_dev) or (any(abs(x) > 1e200 for x in valid_rates) and abs(std_dev) > 1e200):
             raise OverflowError("Overflow encountered in standard deviation calculation")
         mean_val = statistics.mean(valid_rates)
         if not math.isfinite(mean_val) or abs(mean_val) < 1e-9:
             coef_var = 0.0
         else:
             coef_var = std_dev / mean_val
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
    if n == 0:
         return []

    cross_rates = []
    for i in range(n):
         a = rates1[i]
         b = rates2[i]
         if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
             raise TypeError("rates values must be numeric")
         if not math.isfinite(a) or not math.isfinite(b):
             continue
         if b == 0:
             raise ZeroDivisionError("Cannot divide by zero in rates2")
         cross_rates.append(a / b)

    if len(cross_rates) < 2:
         return []

    changes = []
    for i in range(1, len(cross_rates)):
         c = cross_rates[i] - cross_rates[i-1]
         if math.isfinite(c):
             changes.append(c)

    if not changes:
         return []

    min_c = min(changes)
    max_c = max(changes)

    interval_size = (max_c - min_c) / 13
    if not math.isfinite(interval_size) or interval_size == 0:
         interval_size = 0.0001 # Fallback to prevent divide by zero or invalid intervals
         min_c = 0.0
         max_c = 0.0

    ranges = []
    for i in range(13):
         start_val = min_c + i * interval_size
         end_val = start_val + interval_size
         ranges.append({"start": start_val, "end": end_val, "count": 0})

    for c in changes:
         if not math.isfinite(c):
             continue
         index = int((c - min_c) / interval_size)
         if index < 0:
             index = 0
         elif index >= 13:
             index = 12
         ranges[index]["count"] += 1

    return ranges
