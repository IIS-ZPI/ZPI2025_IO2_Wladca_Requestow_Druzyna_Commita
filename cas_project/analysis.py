import statistics

def session_analysis(rates: list) -> tuple:
    """
    Calculates the number of rising, falling, and unchanged sessions.
    """
    if len(rates) < 2:
        return 0, 0, 0
    
    rises, falls, unchanged = 0, 0, 0
    # Start loop from index 1 and compare to index 0
    for i in range(1, len(rates)):
        if rates[i] > rates[i-1]:
            rises += 1
        elif rates[i] < rates[i-1]:
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
    cross_rates = [rates1[i] / rates2[i] for i in range(n)]
    
    changes = []
    for i in range(1, n):
        changes.append(cross_rates[i] - cross_rates[i-1])
        
    if not changes: return []
    
    min_c = min(changes)
    max_c = max(changes)
    
    interval_size = (max_c - min_c) / 13
    if interval_size == 0:
         interval_size = 0.0001 # Fallback to prevent divide by zero
         
    ranges = []
    for i in range(13):
         start_val = min_c + i * interval_size
         end_val = start_val + interval_size
         ranges.append({"start": start_val, "end": end_val, "count": 0})
         
    for c in changes:
         for i, r in enumerate(ranges):
             # For the very last interval, we must handle boundary inclusion (c <= end)
             if r["start"] <= c < r["end"]:
                 r["count"] += 1
                 break
             if i == 12 and c == r["end"]:
                 r["count"] += 1
                 break
                 
    return ranges
