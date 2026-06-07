import csv
import os

def export_to_csv(data: list, filename: str):
    """
    Exports a list of dictionaries to a CSV file.
    """
    if not isinstance(filename, str):
         raise TypeError("filename must be a string")

    if not data:
         print("No data available to export.")
         return
         
    keys = data[0].keys()
    try:
         with open(filename, 'w', newline='', encoding='utf-8') as f:
             writer = csv.DictWriter(f, fieldnames=keys)
             writer.writeheader()
             writer.writerows(data)
         print(f"Success: Data successfully exported to {filename}.")
    except PermissionError as e:
         if not os.path.isabs(filename):
             print(f"Failed to export to CSV: {e}")
             return
         raise
    except (IsADirectoryError, FileNotFoundError, OSError):
         raise
