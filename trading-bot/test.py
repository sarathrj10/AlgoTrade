from src.utils.math_helpers import money_to_points

#   target_gap = money_to_points(config.REWARD_RUPEES, config.QUANTITY, config.LOTS, config.RISK_MODE)
# 1. Nifty 50 scenario (1 lot = 75 quantity) in PER_LOT mode
target_gap = money_to_points(1000, 75, 1, "PER_LOT")
sl_gap = money_to_points(500, 75, 1, "PER_LOT")
trail_step = money_to_points(250, 75, 1, "PER_LOT")
print(target_gap) # 13.33
print(sl_gap) # 6.67
print(trail_step) # 3.33

# 2. Nifty 50 scenario (2 lot = 150 quantity) in PER_LOT mode
target_gap = money_to_points(1000, 150, 2, "PER_LOT")
sl_gap = money_to_points(500, 150, 2, "PER_LOT")
trail_step = money_to_points(250, 150, 2, "PER_LOT")
print(target_gap) # 13.33
print(sl_gap) # 6.67
print(trail_step) # 3.33


# 3. Nifty 50 scenario (2 lot = 150 quantity) in TOTAL mode
target_gap = money_to_points(1000, 150, 2, "TOTAL")
sl_gap = money_to_points(500, 150, 2, "TOTAL")
trail_step = money_to_points(250, 150, 2, "TOTAL")
print(target_gap) # 6.67
print(sl_gap) # 3.33
print(trail_step) # 1.67


# 4. TATAMOTORS scenario (1 lot = 800 quantity) in PER_LOT mode
target_gap = money_to_points(1000, 800, 1, "PER_LOT")
sl_gap = money_to_points(500, 800, 1, "PER_LOT")
trail_step = money_to_points(250, 800, 1, "PER_LOT")
print(target_gap) # 1.25
print(sl_gap) # 0.62
print(trail_step) # 0.31