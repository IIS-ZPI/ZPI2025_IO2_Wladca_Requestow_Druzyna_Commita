import sys
from api import fetch_currency_data
from analysis import session_analysis, statistical_measures, distribution_of_changes
from export import export_to_csv

# We define the number of sessions based on working days 
PERIODS = {
    "1": ("1 Week", 5),
    "2": ("2 Weeks", 10),
    "3": ("1 Month", 22),
    "4": ("1 Quarter", 65),
    "5": ("Half a Year", 130),
    "6": ("1 Year", 255)
}

def display_menu():
    print("\n=== Currency Analytics System (CAS) ===")
    print("1. Session Analysis")
    print("2. Statistical Measures")
    print("3. Distribution of Changes")
    print("4. Exit")
    return input("Select an option (1-4): ")

def get_currency():
    return input("Enter Currency Code (e.g., EUR, USD, GBP, CHF): ").strip().upper()

def get_period(limit_to_months=False):
    print("\nSelect Period:")
    for k, v in PERIODS.items():
        if limit_to_months and k not in ["3", "4"]:
             continue
        print(f"{k}. {v[0]}")
    p = input("Select period: ").strip()
    
    if limit_to_months and p not in ["3", "4"]:
         print("Invalid selection. Only Monthly and Quarterly analysis allowed for distribution.")
         return None
         
    if p in PERIODS:
         return PERIODS[p][1]
    print("Invalid selection.")
    return None

def main():
    while True:
        choice = display_menu()
        
        if choice == "4":
            print("Exiting application. Goodbye.")
            sys.exit(0)
            
        elif choice == "1":
            curr = get_currency()
            days = get_period()
            if not days: continue
            
            try:
                rates = fetch_currency_data(curr, days)
                if not rates:
                    print("Error: Unable to fetch data. Try again.")
                    continue
                    
                rises, falls, unchanged = session_analysis(rates)
                print("\n--- Session Analysis Results ---")
                print(f"Currency: {curr}")
                print(f"Rising sessions: {rises}")
                print(f"Falling sessions: {falls}")
                print(f"Unchanged sessions: {unchanged}")
                
                if input("Export results to CSV? (Y/N): ").strip().upper() == 'Y':
                    export_to_csv([
                        {"Metric": "Rising", "Value": rises},
                        {"Metric": "Falling", "Value": falls},
                        {"Metric": "Unchanged", "Value": unchanged}
                    ], f"session_output_{curr}.csv")
            except Exception as e:
                print(f"\nSystem Error: {e}\nTry again.")

        elif choice == "2":
            curr = get_currency()
            days = get_period()
            if not days: continue
            
            try:
                rates = fetch_currency_data(curr, days)
                if not rates:
                    print("Error: Unable to fetch data. Try again.")
                    continue
                    
                stats = statistical_measures(rates)
                print("\n--- Statistical Measures ---")
                print(f"Currency: {curr}")
                for k, v in stats.items():
                    print(f"{k.replace('_', ' ').capitalize()}: {v:.4f}")
                    
                if input("Export results to CSV? (Y/N): ").strip().upper() == 'Y':
                    export_to_csv([{"Metric": k, "Value": v} for k, v in stats.items()], f"stats_output_{curr}.csv")
            except Exception as e:
                print(f"\nSystem Error: {e}\nTry again.")

        elif choice == "3":
            pair = input("Enter Currency Pair (e.g., EUR/USD): ").strip().upper()
            
            # Fixing the bug with redundant or missing characters (double slash test)
            # Zmiana: System automatycznie redukuje wielokrotne ukośniki przed walidacją
            while "//" in pair:
                pair = pair.replace("//", "/")
                
            if pair.count("/") != 1:
                print("Invalid format. Use XXX/YYY format.")
                continue
                
            c1, c2 = pair.split("/")
            if not c1 or not c2:
                print("Invalid format. Missing currency code.")
                continue
            
            days = get_period(limit_to_months=True)
            if not days: continue
            
            try:
                # Short-circuit evaluation. API is called for c2 ONLY if c1 succeeded.
                rates1 = fetch_currency_data(c1, days)
                if not rates1:
                    print(f"Error: Unable to fetch data for {c1}. Try again.")
                    continue
                    
                rates2 = fetch_currency_data(c2, days)
                if not rates2:
                    print(f"Error: Unable to fetch data for {c2}. Try again.")
                    continue
                
                ranges = distribution_of_changes(rates1, rates2)
                
                if not ranges:
                    print("Not enough data to calculate distribution.")
                    continue
                    
                print(f"\n--- Distribution of Changes for {pair} ---")
                print(f"{'Range Start':>12} - {'Range End':<12} | {'Count':^5} | Histogram")
                print("-" * 65)
                
                csv_data = []
                for r in ranges:
                    start_str = f"{r['start']:.4f}"
                    end_str = f"{r['end']:.4f}"
                    stars = "*" * r['count']
                    print(f"{start_str:>12} - {end_str:<12} | {r['count']:^5} | {stars}")
                    csv_data.append({"Range Start": start_str, "Range End": end_str, "Count": r['count']})
                    
                if input("Export results to CSV? (Y/N): ").strip().upper() == 'Y':
                    export_to_csv(csv_data, f"distribution_output_{c1}_{c2}.csv")
            except Exception as e:
                print(f"\nSystem Error: {e}\nTry again.")

if __name__ == "__main__":
    main()