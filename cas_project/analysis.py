import math
import statistics
from models import SessionResult, StatisticalResult, DistributionRange

def _get_val(item):
    if hasattr(item, 'mid'):
        return item.mid
    return item

def session_analysis(rates: list) -> SessionResult:
    if not isinstance(rates, list):
        raise TypeError("rates must be a list")
    if len(rates) < 2:
        return SessionResult(0, 0, 0)

    rises, falls, unchanged = 0, 0, 0
    for i in range(1, len(rates)):
        prev = _get_val(rates[i-1])
        curr = _get_val(rates[i])

        if not isinstance(prev, (int, float)) or not isinstance(curr, (int, float)):
            raise TypeError("rates mid values must be numeric")
        if math.isnan(prev) or math.isnan(curr):
            continue

        if curr > prev:
            rises += 1
        elif curr < prev:
            falls += 1
        else:
            unchanged += 1

    return SessionResult(rising=rises, falling=falls, unchanged=unchanged)

def statistical_measures(rates: list) -> StatisticalResult:
    target_rates = rates[1:] if len(rates) > 1 else rates

    if not target_rates:
         return StatisticalResult(0.0, 0.0, 0.0, 0.0)

    valid_rates = []
    for x in target_rates:
         val = _get_val(x)
         if not isinstance(val, (int, float)):
             raise TypeError("rates items must be numeric")
         if math.isfinite(val):
             valid_rates.append(float(val))

    if not valid_rates:
         return StatisticalResult(0.0, 0.0, 0.0, 0.0)

    n = len(valid_rates)
    median = statistics.median(valid_rates)

    try:
         mode = statistics.mode(valid_rates)
    except statistics.StatisticsError:
         mode = valid_rates[0]

    if n > 1:
         std_dev = statistics.stdev(valid_rates)
         if not math.isfinite(std_dev):
             raise OverflowError("Calculation exceeded maximum bounds")
         variance = std_dev * std_dev
         if not math.isfinite(variance):
             raise OverflowError("Calculation exceeded maximum bounds")
         mean_val = statistics.mean(valid_rates)
         if not math.isfinite(mean_val) or abs(mean_val) < 1e-9:
             coef_var = 0.0
         else:
             coef_var = std_dev / mean_val
    else:
         std_dev, coef_var = 0.0, 0.0

    return StatisticalResult(
         median=round(median, 4),
         mode=round(mode, 4),
         standard_deviation=round(std_dev, 4),
         coefficient_of_variation=round(coef_var, 4)
    )

def distribution_of_changes(rates1: list, rates2: list) -> list:
    n = min(len(rates1), len(rates2))
    if n == 0:
         return []

    cross_rates = []
    for i in range(n):
         a = _get_val(rates1[i])
         b = _get_val(rates2[i])
         if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
             raise TypeError("rates mid values must be numeric")
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

    ranges = []
    if min_c == max_c:
         center_value = min_c
         magnitude = abs(center_value) if abs(center_value) > 0 else 1.0
         interval_size = magnitude * 0.0001
         start_base = center_value - 6.5 * interval_size
         for i in range(13):
             start_val = start_base + i * interval_size
             end_val = start_val + interval_size
             ranges.append(DistributionRange(start=start_val, end=end_val, count=0))
    else:
         interval_size = (max_c - min_c) / 13
         if not math.isfinite(interval_size) or interval_size == 0:
             fallback_mag = max(abs(min_c), abs(max_c), 1.0)
             interval_size = fallback_mag * 0.0001
         for i in range(13):
             start_val = min_c + i * interval_size
             end_val = start_val + interval_size
             ranges.append(DistributionRange(start=start_val, end=end_val, count=0))

    for c in changes:
         if not math.isfinite(c):
             continue
         if min_c == max_c:
             index = int((c - (center_value - 6.5 * interval_size)) / interval_size)
         else:
             index = int((c - min_c) / interval_size)
         if index < 0:
             index = 0
         elif index >= 13:
             index = 12
         ranges[index].count += 1

    return ranges