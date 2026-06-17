import pytest
from unittest.mock import patch, MagicMock
import sys
from main import get_currency, get_period, display_menu, main

# =====================================================================
# NEW EXTENDED TEST SUITE (30 TESTS TOTAL)
# =====================================================================

# --- HELPER FIX FOR INFINITE LOOPS ---
def setup_exit(mock_exit):
    mock_exit.side_effect = SystemExit

# 13. Test: Currency with numbers (Should pass to API and fail there)
@patch("builtins.input", return_value="USD123")
def test_get_currency_with_numbers(mock_input):
    assert get_currency() == "USD123"

# 14. Test: Lowercase currency conversion
@patch("builtins.input", return_value="pln")
def test_get_currency_lowercase(mock_input):
    assert get_currency() == "PLN"

# 15. Test: Period selection - Out of range (High)
@patch("builtins.input", return_value="7")
def test_get_period_overflow(mock_input):
    assert get_period() is None

# 16. Test: Period selection - Out of range (Low)
@patch("builtins.input", return_value="0")
def test_get_period_underflow(mock_input):
    assert get_period() is None

# 17. Test: Period selection - Negative number
@patch("builtins.input", return_value="-1")
def test_get_period_negative(mock_input):
    assert get_period() is None

# 18. Test: Distribution period - Selecting non-allowed option (1 Week)
@patch("builtins.input", return_value="1")
def test_get_period_dist_invalid_short(mock_input):
    assert get_period(limit_to_months=True) is None

# 19. Test: Distribution period - Selecting allowed option (1 Month)
@patch("builtins.input", return_value="3")
def test_get_period_dist_valid_month(mock_input):
    assert get_period(limit_to_months=True) == 22

# 20. Test: Main Loop - Option 1: API returns None (Handled)
@patch("main.fetch_currency_data", return_value=None)
@patch("builtins.input", side_effect=["1", "USD", "1", "4"])
@patch("main.sys.exit")
def test_main_api_returns_none(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 21. Test: Main Loop - Option 1: API returns empty list (Handled)
@patch("main.fetch_currency_data", return_value=[])
@patch("builtins.input", side_effect=["1", "USD", "1", "4"])
@patch("main.sys.exit")
def test_main_api_returns_empty(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 22. Test: Main Loop - Option 2: Export declined (N)
@patch("main.fetch_currency_data", return_value=[4.0, 4.1])
@patch("builtins.input", side_effect=["2", "USD", "1", "N", "4"])
@patch("main.sys.exit")
def test_main_stats_no_export(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 23. Test: Main Loop - Option 3: Malformed pair (Empty string)
@patch("builtins.input", side_effect=["3", "", "4"])
@patch("main.sys.exit")
def test_main_dist_empty_pair(mock_exit, mock_input):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 24. Test: Main Loop - Option 3: Wrong separator (EUR-USD)
@patch("builtins.input", side_effect=["3", "EUR-USD", "4"])
@patch("main.sys.exit")
def test_main_dist_wrong_separator(mock_exit, mock_input):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 25. Test: Main Loop - Option 3: Double slashes (EUR//USD)
@patch("main.fetch_currency_data", side_effect=[[], []])
@patch("builtins.input", side_effect=["3", "EUR//USD", "4"])
@patch("main.sys.exit")
def test_main_dist_double_slash(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 26. Test: Main Loop - Option 1: Extreme currency code length
@patch("main.fetch_currency_data", return_value=[])
@patch("builtins.input", side_effect=["1", "VERYLONGCODE", "1", "4"])
@patch("main.sys.exit")
def test_main_long_currency_code(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 27. Test: Main Loop - Rapid fire invalid menu options
@patch("builtins.input", side_effect=["9", "0", "-5", "exit", "4"])
@patch("main.sys.exit")
def test_main_rapid_invalid_menu(mock_exit, mock_input):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 28. Test: Option 2 - API Failure mid-process
@patch("main.fetch_currency_data", side_effect=Exception("Timeout"))
@patch("builtins.input", side_effect=["2", "USD", "1", "4"])
@patch("main.sys.exit")
def test_main_stats_api_timeout(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()

# 29. Test: Option 3 - API Failure on first currency, second not called
@patch("main.fetch_currency_data", return_value=None)
@patch("builtins.input", side_effect=["3", "EUR/USD", "3", "4"])
@patch("main.sys.exit")
def test_main_dist_first_api_fails(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()
    assert mock_fetch.call_count == 1 # Second call should be skipped

# 30. Test: Full Cycle - Option 1 then Option 2 then Exit
@patch("main.fetch_currency_data", return_value=[4.0, 4.1, 4.2])
@patch("builtins.input", side_effect=["1", "USD", "1", "N", "2", "EUR", "1", "N", "4"])
@patch("main.sys.exit")
def test_main_multi_step_workflow(mock_exit, mock_input, mock_fetch):
    setup_exit(mock_exit)
    with pytest.raises(SystemExit):
        main()
    assert mock_fetch.call_count == 2