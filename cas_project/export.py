import csv

def export_to_csv(data, filename: str):
    """
    Exports a list of dictionaries to a CSV file gracefully handling errors.
    """
    # Filename validation
    if not isinstance(filename, str):
         raise TypeError("Filename must be a string")
         
    if not data:
         print("No data available to export.")
         return
         
    # Converting iterators/generators to a list and verifying structure
    try:
        data_list = list(data)
    except TypeError:
        raise TypeError("Data must be an iterable")
        
    if not data_list:
        return
        
    if not isinstance(data_list[0], dict):
         raise AttributeError("Data elements must be dictionaries")
         
    # Preventing nested structures leaks (dict/list in CSV)
    for row in data_list:
        for val in row.values():
            if isinstance(val, (dict, list, tuple)):
                raise ValueError("Nested structures are not allowed in flat CSV export.")
         
    keys = data_list[0].keys()
    
    # Catching critical I/O errors at the OS level
    try:
         with open(filename, 'w', newline='', encoding='utf-8') as f:
              writer = csv.DictWriter(f, fieldnames=keys)
              writer.writeheader()
              writer.writerows(data_list)
         print(f"Success: Data successfully exported to {filename}.")
    except PermissionError:
         print(f"Error: Permission denied. Cannot write to {filename}.")
    except OSError as e:
         print(f"System Error during export: {e}")