import csv

def export_to_csv(data: list, filename: str):
    """
    Exports a list of dictionaries to a CSV file.
    """
    if not data:
         print("No data available to export.")
         return
         
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
         writer = csv.DictWriter(f, fieldnames=keys)
         writer.writeheader()
         writer.writerows(data)
    print(f"Success: Data successfully exported to {filename}.")
