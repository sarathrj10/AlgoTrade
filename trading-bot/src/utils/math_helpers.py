import math

def money_to_points(value, quantity, lots=1, mode="PER_LOT"):
    if mode.upper() == "PER_LOT":
        total = value * lots
    else:
        total = value
    return total / quantity

def trailing_steps(base_sl, ltp, first_target, step_size):
    points_above_target = ltp - first_target
    if points_above_target <= 0:
        return base_sl
    steps = math.floor(points_above_target / step_size)
    return base_sl + steps * step_size
