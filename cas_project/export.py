import csv
import json

def export_to_csv(data: list, filename: str):
    """
    Exports a list of dictionaries to a CSV file.
    """
    if not isinstance(filename, str):
         raise TypeError("filename must be a string")

    if not data:
         print("No data available to export.")
         return

    if not isinstance(data, list):
         print("Invalid data schema: expected a list of dictionaries.")
         return

    first_row = data[0]
    if not isinstance(first_row, dict):
         print("Invalid data schema: first row must be a dictionary.")
         return

    if not first_row:
         print("Invalid data schema: first row must contain at least one column.")
         return

    if not all(isinstance(key, str) for key in first_row.keys()):
         print("Invalid data schema: CSV header keys must be strings.")
         return

    fieldnames = list(first_row.keys())
    sanitized_rows = []

    for row_index, row in enumerate(data):
         if not isinstance(row, dict):
             print(f"Invalid data schema: row {row_index} is not a dictionary.")
             return
         if set(row.keys()) != set(fieldnames):
             print("Invalid data schema: inconsistent row keys detected.")
             return

         sanitized_row = {}
         for key in fieldnames:
             value = row.get(key)
             if value is None or isinstance(value, (str, int, float, bool)):
                 sanitized_row[key] = value
             elif isinstance(value, (list, dict, tuple, set)):
                 try:
                     sanitized_row[key] = json.dumps(value, ensure_ascii=False)
                 except (TypeError, ValueError):
                     print(f"Invalid data schema: unsupported nested structure in row {row_index}, column '{key}'.")
                     return
             else:
                 print(f"Invalid data schema: unsupported type in row {row_index}, column '{key}'.")
                 return
         sanitized_rows.append(sanitized_row)

    try:
         with open(filename, 'w', newline='', encoding='utf-8') as f:
             writer = csv.DictWriter(f, fieldnames=fieldnames)
             writer.writeheader()
             writer.writerows(sanitized_rows)
         print(f"Success: Data successfully exported to {filename}.")
    except PermissionError as e:
         print(f"Failed to export to CSV: Permission denied - {e}")
    except OSError as e:
         print(f"Failed to export to CSV: {e}")
