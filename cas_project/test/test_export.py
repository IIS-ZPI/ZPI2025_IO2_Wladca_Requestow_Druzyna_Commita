import pytest
import csv
import os
from unittest.mock import patch
from export import export_to_csv  # Ensure the module name matches your actual file (e.g., export or exporty)

# =====================================================================
# BLOCK 1: DATA STRUCTURE MUTILATION (Fuzzing)
# Testing if export_to_csv correctly rejects invalid data structures.
# =====================================================================

DATA_POISONING_PAYLOADS = [
    # 1. Root structure is not a list/iterable
    (12345, TypeError),
    (True, TypeError),
    # Converting dict to list gives a list of keys (strings), not dicts, so it raises AttributeError
    ({"key": "val"}, AttributeError),  
    ("string_data", AttributeError),   
    (set([1, 2, 3]), AttributeError),  

    # 2. Structure is a list, but elements are NOT dicts
    ([1, 2, 3], AttributeError),
    ([None], AttributeError),
    ([["a", "b"]], AttributeError),
    ([True, False], AttributeError),
    ([4.15], AttributeError),

    # 3. First element is a dict, but subsequent elements are garbage
    # Loops will attempt to call .values() on these invalid types
    ([{"a": 1}, None], AttributeError),
    ([{"a": 1}, [1, 2]], AttributeError),
    ([{"a": 1}, 1234], AttributeError),
    ([{"a": 1}, "string"], AttributeError),

    # 4. Schema Inconsistency (Extremely common in API data)
    ([{"a": 1}, {"a": 1, "b": 2}], ValueError),  # ValueError: dict contains fields not in fieldnames
]

@pytest.mark.parametrize("payload, expected_exc", DATA_POISONING_PAYLOADS)
def test_export_data_structure_fuzzing(tmp_path, payload, expected_exc):
    """Verifies that the export gracefully rejects malformed inputs with correct exceptions."""
    file_path = tmp_path / "fuzz.csv"
    with pytest.raises(expected_exc):
        export_to_csv(payload, str(file_path))


# =====================================================================
# BLOCK 2: FILENAME PARAMETER MUTILATION
# =====================================================================

FILENAME_PAYLOADS = [
    ([{"a": 1}], None, TypeError),
    ([{"a": 1}], 1234, TypeError),
    ([{"a": 1}], True, TypeError),
    ([{"a": 1}], ["test.csv"], TypeError),
    ([{"a": 1}], {"file": "test.csv"}, TypeError),
]

@pytest.mark.parametrize("data, bad_filename, expected_exc", FILENAME_PAYLOADS)
def test_export_filename_type_fuzzing(data, bad_filename, expected_exc):
    """Tests vulnerability to bad argument types for the filename."""
    with pytest.raises(expected_exc):
        export_to_csv(data, bad_filename)


# =====================================================================
# BLOCK 3: FILESYSTEM & OS FAILURES (I/O Mocking)
# =====================================================================

FS_FAILURES = [
    PermissionError("Access denied"),
    IsADirectoryError("Is a directory"),
    FileNotFoundError("No such file or directory"),
    OSError("Disk full"),
]

@pytest.mark.parametrize("mock_exc", FS_FAILURES)
def test_export_os_level_failures_handled(mock_exc):
    """
    Simulates catastrophic OS events.
    Verifies that export_to_csv catches these exceptions and prevents application crashes.
    """
    with patch("builtins.open", side_effect=mock_exc):
        try:
            export_to_csv([{"a": 1}], "C:/protected_folder/test.csv")
        except Exception as e:
            pytest.fail(f"APPLICATION CRASHED: export_to_csv failed to gracefully handle {type(e).__name__}!")


# =====================================================================
# BLOCK 4: LOGICAL BEHAVIORS & DATA DEFENSE
# =====================================================================

def test_export_generator_success(tmp_path):
    """SUCCESS TEST: Verifies that Iterators/Generators are safely converted to lists."""
    gen = (x for x in [{"a": 1}, {"a": 2}])
    file_path = tmp_path / "gen.csv"
    
    # This should no longer crash, it should succeed
    export_to_csv(gen, str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "a" in content and "1" in content and "2" in content


def test_export_nested_structures_blocked(tmp_path):
    """
    DEFENSE TEST: Ensures that dictionaries with nested structures raise a ValueError
    instead of leaking raw string representations into the CSV.
    """
    data = [{"Metric": "Stats", "Value": {"nested": [1, 2, 3]}}]
    file_path = tmp_path / "nested.csv"
    
    with pytest.raises(ValueError, match="Nested structures are not allowed"):
        export_to_csv(data, str(file_path))


def test_export_empty_data_handled_gracefully():
    """Valid edge case: Data is empty. Code correctly checks 'if not data:'"""
    # This should NOT crash
    export_to_csv([], "does_not_matter.csv")
    export_to_csv(None, "does_not_matter.csv")


# =====================================================================
# BLOCK 5: THE CRITICAL FAILURE TEST
# =====================================================================

def test_export_handles_permission_error_gracefully():
    """
    CRITICAL FAILURE TEST:
    Asserts that the application safely handles Access Denied errors
    without crashing the entire program.
    """
    with patch("builtins.open", side_effect=PermissionError):
        try:
            export_to_csv([{"a": 1}], "restricted.csv")
        except PermissionError:
            pytest.fail("APPLICATION CRASHED: export_to_csv failed to gracefully handle an OS PermissionError!")