import time
from src.utils.file_helpers import save_state

class TrailingSL:
    def __init__(self, kite_client, symbol, quantity, config, state):
        self.kite = kite_client
        self.symbol = symbol
        self.quantity = quantity
        self.config = config
        self.state = state

    def place_initial_sl(self, sl_trigger):
        limit = sl_trigger - self.config.ORDER_BUFFER
        oid = self.kite.place_sl_order(self.symbol, self.quantity, sl_trigger, limit, self.config.PRODUCT)
        self.state['sl_order_id'] = oid
        self.state['sl_trigger'] = sl_trigger
        self.state['mod_count'] = 0
        self.state['last_sl_update_time'] = time.time()
        save_state(self.state, self.config.STATE_FILE)
        return oid

    def modify_sl(self, new_trigger):
        now = time.time()
        if now - self.state.get('last_sl_update_time', 0) < self.config.THROTTLE_SECONDS:
            return False

        oid = self.state.get('sl_order_id')
        if oid and self.state.get('mod_count', 0) < self.config.MAX_MODIFY_BEFORE_RECREATE:
            limit = new_trigger - self.config.ORDER_BUFFER
            self.kite.modify_order(oid, new_trigger, limit)
            self.state['mod_count'] += 1
            self.state['sl_trigger'] = new_trigger
            self.state['last_sl_update_time'] = now
            save_state(self.state, self.config.STATE_FILE)
            return True
        # recreate order if mod_count exceeded
        if oid:
            self.kite.cancel_order(oid)
        self.place_initial_sl(new_trigger)
        return True
