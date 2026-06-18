import csv
import json
from dataclasses import is_dataclass, fields, asdict


def export_to_csv(data, filename: str) -> bool:
    """
    Exports an iterable of dataclasses or dictionaries to a CSV file.
    Returns True on success and False on failure.
    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")

    if data is None:
        print("No data available to export.")
        return False

    try:
        iterator = iter(data)
    except TypeError:
        print("Invalid data schema: expected an iterable.")
        return False

    try:
        first_row = next(iterator)
    except StopIteration:
        print("No data available to export.")
        return False

    if is_dataclass(first_row):
        fieldnames = [f.name for f in fields(first_row)]
    elif isinstance(first_row, dict):
        if not first_row:
            print("Invalid data schema: first row must contain at least one column.")
            return False
        if not all(isinstance(key, str) for key in first_row.keys()):
            print("Invalid data schema: CSV header keys must be strings.")
            return False
        fieldnames = list(first_row.keys())
    else:
        print("Invalid data schema: expected a dataclass instance or dictionary.")
        return False

    def sanitize_value(value, row_index, key):
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, (list, dict, tuple, set)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError):
                raise ValueError(f"Unsupported nested structure in row {row_index}, column '{key}'.")
        raise TypeError(f"Unsupported type in row {row_index}, column '{key}'.")

    def generate_sanitized_rows():
        def sanitize_row(row_obj, row_index):
            if is_dataclass(row_obj):
                row_dict = asdict(row_obj)
            elif isinstance(row_obj, dict):
                row_dict = row_obj
            else:
                raise TypeError(f"Row {row_index} is not a dataclass or dictionary.")

            if set(row_dict.keys()) != set(fieldnames):
                raise ValueError("Invalid data schema: inconsistent row keys detected.")

            sanitized = {}
            for key in fieldnames:
                sanitized[key] = sanitize_value(row_dict.get(key), row_index, key)
            return sanitized

        yield sanitize_row(first_row, 0)
        for row_index, row_obj in enumerate(iterator, start=1):
            yield sanitize_row(row_obj, row_index)

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(generate_sanitized_rows())
    except (TypeError, ValueError) as e:
        print(f"Invalid data schema: {e}")
        return False
    except PermissionError as e:
        print(f"Failed to export to CSV: Permission denied - {e}")
        return False
    except OSError as e:
        print(f"Failed to export to CSV: {e}")
        return False

    print(f"Success: Data successfully exported to {filename}.")
    return True