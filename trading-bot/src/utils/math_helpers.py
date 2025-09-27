import math

def money_to_points(value, quantity, lots=1, mode="PER_LOT"):
    if mode.upper() == "PER_LOT":
        total = value * lots
    else:
        total = value
    return round(total / quantity, 2)

def trailing_steps(base_sl, ltp, first_target, step_size):
    """
    Calculate new stop-loss based on trailing step logic.
    
    Args:
        base_sl: Current stop-loss level
        ltp: Current Last Traded Price
        first_target: The first target price level
        step_size: How many points above first_target before moving SL
    
    Returns:
        float: New stop-loss level
    """
    points_above_target = ltp - first_target
    if points_above_target <= 0:
        return base_sl
    if step_size <= 0:
        return base_sl
    steps = math.floor(points_above_target / step_size)
    new_sl = base_sl + (steps * step_size)
    return new_sl
