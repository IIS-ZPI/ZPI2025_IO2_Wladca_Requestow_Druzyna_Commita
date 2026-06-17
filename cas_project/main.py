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

        if choice == "1":
            curr = get_currency()
            days = get_period()
            if not days: continue

            try:
                rates = fetch_currency_data(curr, days)
                if not rates:
                    print("Error: Unable to fetch data. Try again.")
                    continue

                session_result = session_analysis(rates)
                print("\n--- Session Analysis Results ---")
                print(f"Currency: {curr}")
                print(f"Rising sessions: {session_result.rising}")
                print(f"Falling sessions: {session_result.falling}")
                print(f"Unchanged sessions: {session_result.unchanged}")

                if input("Export results to CSV? (Y/N): ").strip().upper() == 'Y':
                    if not export_to_csv([session_result], f"session_output_{curr}.csv"):
                        print("Export failed.")
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
                print(f"Median: {stats.median:.4f}")
                print(f"Mode: {stats.mode:.4f}")
                print(f"Standard Deviation: {stats.standard_deviation:.4f}")
                print(f"Coefficient of Variation: {stats.coefficient_of_variation:.4f}")

                if input("Export results to CSV? (Y/N): ").strip().upper() == 'Y':
                    if not export_to_csv([stats], f"stats_output_{curr}.csv"):
                        print("Export failed.")
            except Exception as e:
                print(f"\nSystem Error: {e}\nTry again.")

        elif choice == "3":
            pair = input("Enter Currency Pair (e.g., EUR/USD): ").strip().upper()
            try:
                c1, c2 = [segment.strip() for segment in pair.split("/")]
            except ValueError:
                print("Invalid format. Use XXX/YYY format.")
                continue
            if not c1 or not c2:
                print("Invalid format. Use XXX/YYY format.")
                continue
            c1, c2 = parts

            days = get_period(limit_to_months=True)
            if not days: continue

            try:
                rates1 = fetch_currency_data(c1, days)
                if not rates1 or len(rates1) < 2:
                    print(f"Error: Unable to fetch valid/sufficient data for the first currency ({c1}).")
                    continue

                rates2 = fetch_currency_data(c2, days)
                if not rates2 or len(rates2) < 2:
                    print(f"Error: Unable to fetch valid/sufficient data for the second currency ({c2}).")
                    continue

                ranges = distribution_of_changes(rates1, rates2)
                print(f"\n--- Distribution of Changes for {pair} ---")
                print(f"{'Range Start':>12} - {'Range End':<12} | {'Count':^5} | Histogram")
                print("-" * 65)

                for r in ranges:
                    start_str = f"{r.start:.4f}"
                    end_str = f"{r.end:.4f}"
                    stars = "*" * r.count
                    print(f"{start_str:>12} - {end_str:<12} | {r.count:^5} | {stars}")

                if input("Export results to CSV? (Y/N): ").strip().upper() == 'Y':
                    if not export_to_csv(ranges, f"distribution_output_{c1}_{c2}.csv"):
                        print("Export failed.")
            except Exception as e:
                print(f"\nSystem Error: {e}\nTry again.")
        else:
            print("Invalid input, please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
