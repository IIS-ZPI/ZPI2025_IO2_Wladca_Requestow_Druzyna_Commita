import pytest
import csv
import os
from unittest.mock import patch
from export import export_to_csv

# =====================================================================
# BLOCK 1: DATA STRUCTURE MUTILATION (Fuzzing)
# Current export.py assumes data[0].keys() will always work.
# =====================================================================

DATA_POISONING_PAYLOADS = [
    # 1. Root structure is not a list/iterable
    (12345, TypeError),
    (True, TypeError),
    ({"key": "val"}, KeyError),  # Indexing [0] on a dict raises KeyError
    ("string_data", AttributeError),  # string[0] is 's', 's'.keys() throws AttributeError
    (set([1, 2, 3]), TypeError),  # Sets do not support indexing

    # 2. Structure is a list, but elements are NOT dicts
    ([1, 2, 3], AttributeError),
    ([None], AttributeError),
    ([["a", "b"]], AttributeError),
    ([True, False], AttributeError),
    ([4.15], AttributeError),

    # 3. First element is a dict, but subsequent elements are garbage
    ([{"a": 1}, None], AttributeError),
    ([{"a": 1}, [1, 2]], AttributeError),
    ([{"a": 1}, 1234], AttributeError),
    ([{"a": 1}, "string"], AttributeError),

    # 4. Schema Inconsistency (Extremely common in API data)
    ([{"a": 1}, {"a": 1, "b": 2}], ValueError),  # ValueError: dict contains fields not in fieldnames
]


@pytest.mark.parametrize("payload, _", DATA_POISONING_PAYLOADS)
def test_export_data_structure_fuzzing(tmp_path, payload, _):
    """
    Bombards export_to_csv with 15 malformed data structures.
    The function should handle invalid schema gracefully and not crash.
    """
    file_path = tmp_path / "fuzz.csv"
    export_to_csv(payload, str(file_path))


# =====================================================================
# BLOCK 2: FILENAME PARAMETER MUTILATION
# Current export.py assumes filename is a valid string.
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
# Current export.py has NO try...except block around with open()
# =====================================================================

FS_FAILURES = [
    (PermissionError("Access denied"), PermissionError),
    (IsADirectoryError("Is a directory"), IsADirectoryError),
    (FileNotFoundError("No such file or directory"), FileNotFoundError),
    (OSError("Disk full"), OSError),
]


@pytest.mark.parametrize("mock_exc, _", FS_FAILURES)
def test_export_os_level_failures(mock_exc, _):
    """
    Simulates catastrophic OS events (e.g., trying to save to a read-only drive).
    The application should catch file I/O failures and continue running.
    """
    with patch("builtins.open", side_effect=mock_exc):
        export_to_csv([{"a": 1}], "C:/protected_folder/test.csv")


# =====================================================================
# BLOCK 4: LOGICAL BUGS & DATA LEAKS
# =====================================================================

def test_export_generator_crash(tmp_path):
    """CRASH: Iterators/Generators don't have __getitem__[0] support."""
    gen = (x for x in [{"a": 1}, {"a": 2}])
    file_path = tmp_path / "gen.csv"
    export_to_csv(gen, str(file_path))


def test_export_nested_structures_leak(tmp_path):
    """
    LOGICAL BUG: Values contain nested dictionaries.
    export_to_csv should serialize nested structures safely rather than writing Python repr.
    """
    data = [{"Metric": "Stats", "Value": {"nested": [1, 2, 3]}}]
    file_path = tmp_path / "nested.csv"
    export_to_csv(data, str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert '"{""nested"": [1, 2, 3]}"' in content, "Data should be serialized as JSON, not Python repr."
        assert "{'nested': [1, 2, 3]}" not in content, "Data leak: nested objects printed as raw strings."


def test_export_empty_data_handled_gracefully():
    """Valid edge case: Data is empty. Code correctly checks 'if not data:'"""
    # This should NOT crash
    export_to_csv([], "does_not_matter.csv")
    export_to_csv(None, "does_not_matter.csv")


# =====================================================================
# BLOCK 5: THE GUARANTEED FAILURE (Red Test)
# This test asserts that the application SHOULD handle Permission Errors gracefully.
# Since export.py does NOT handle it, this test will FAIL in Pytest.
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