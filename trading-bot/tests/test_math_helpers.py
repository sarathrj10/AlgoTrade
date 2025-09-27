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


@pytest.mark.parametrize("scenario, base_sl, current_ltp, first_target, trail_step, expected", [
    # Based on example: Buy at 20, SL at 13, First target at 34, base_sl moved to 27 (midpoint)
    # Trail step is 3.34, so SL moves up every 3.34 points above first target
    
    # Scenario 1: NIFTY50 trailing after first target hit
    ("LTP just above target - no trail yet", 27, 35, 34, 3.34, 27),      # LTP 35: 1 point above target, less than trail_step
    ("LTP 2 points above target - no trail", 27, 36, 34, 3.34, 27),     # LTP 36: 2 points above target, less than trail_step  
    ("LTP 3 points above target - no trail", 27, 37, 34, 3.34, 27),     # LTP 37: 3 points above target, less than trail_step
    ("LTP 4 points above target - trail kicks in", 27, 38, 34, 3.34, 30.34),  # LTP 38: 4 points above, exceeds trail_step, SL moves to 27+3.34=30.34
    
    # Additional scenarios for comprehensive testing
    ("LTP at exactly first target", 27, 34, 34, 3.34, 27),              # At target level, no trailing
    ("LTP below first target", 27, 33, 34, 3.34, 27),                   # Below target, no trailing
    ("LTP much higher - multiple trail steps", 27, 45, 34, 3.34, 37.02), # LTP 45: (45-34)/3.34 = 3.29 steps, so 27+(3*3.34)=37.02
])
def test_trailing_steps_scenarios(scenario, base_sl, current_ltp, first_target, trail_step, expected):
    """
    Test trailing stop-loss logic with various market scenarios
    
    The trailing_steps function should:
    1. Return base_sl if LTP <= first_target (no trailing below target)
    2. Calculate steps above first_target: (LTP - first_target) // trail_step
    3. Return base_sl + (full_steps * trail_step)
    """
    result = trailing_steps(base_sl, current_ltp, first_target, trail_step)
    assert abs(result - expected) < 0.01, f"Failed in scenario: {scenario}. Expected {expected}, got {result}"

