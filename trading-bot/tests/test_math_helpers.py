import pytest
from src.utils.math_helpers import money_to_points, trailing_steps

@pytest.mark.parametrize("scenario, value, quantity, lots, mode, expected", [
    # Scenario 1: Nifty 50 (1 lot = 75 quantity) in PER_LOT mode
    ("Nifty50 1 lot target_gap", 1000, 75, 1, "PER_LOT", 13.33),
    ("Nifty50 1 lot sl_gap", 500, 75, 1, "PER_LOT", 6.67),
    ("Nifty50 1 lot trail_step", 250, 75, 1, "PER_LOT", 3.33),
    
    # Scenario 2: Nifty 50 (2 lots = 150 quantity) in PER_LOT mode
    ("Nifty50 2 lots target_gap", 1000, 150, 2, "PER_LOT", 13.33),
    ("Nifty50 2 lots sl_gap", 500, 150, 2, "PER_LOT", 6.67),
    ("Nifty50 2 lots trail_step", 250, 150, 2, "PER_LOT", 3.33),
    
    # Scenario 3: Nifty 50 (2 lots = 150 quantity) in TOTAL mode
    ("Nifty50 2 lots TOTAL target_gap", 1000, 150, 2, "TOTAL", 6.67),
    ("Nifty50 2 lots TOTAL sl_gap", 500, 150, 2, "TOTAL", 3.33),
    ("Nifty50 2 lots TOTAL trail_step", 250, 150, 2, "TOTAL", 1.67),
    
    # Scenario 4: TATAMOTORS (1 lot = 800 quantity) in PER_LOT mode
    ("TATAMOTORS 1 lot target_gap", 1000, 800, 1, "PER_LOT", 1.25),
    ("TATAMOTORS 1 lot sl_gap", 500, 800, 1, "PER_LOT", 0.62),
    ("TATAMOTORS 1 lot trail_step", 250, 800, 1, "PER_LOT", 0.31),
])
def test_money_to_points_scenarios(scenario, value, quantity, lots, mode, expected):
    """
    Test various real-world trading scenarios using parameterized testing
    """
    result = money_to_points(value, quantity, lots, mode)
    assert result == expected, f"Failed in scenario: {scenario}"

