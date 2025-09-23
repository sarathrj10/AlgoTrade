from kiteconnect import KiteConnect
from .auth import ZerodhaAuth

class KiteClient:
    def __init__(self, api_key=None, access_token=None):
        # If credentials not provided, use auth module
        if not api_key or not access_token:
            auth = ZerodhaAuth()
            credentials = auth.get_credentials()
            api_key = credentials["api_key"]
            access_token = credentials["access_token"]
            
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def get_positions(self):
        return self.kite.positions()

    def place_sl_order(self, symbol, quantity, trigger, limit, product):
        return self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange="NFO",
            tradingsymbol=symbol,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_SL,
            product=product,
            trigger_price=trigger,
            price=limit,
            validity=self.kite.VALIDITY_DAY
        )

    def modify_order(self, order_id, trigger, limit):
        return self.kite.modify_order(
            variety=self.kite.VARIETY_REGULAR,
            order_id=order_id,
            trigger_price=trigger,
            price=limit
        )

    def cancel_order(self, order_id):
        return self.kite.cancel_order(variety=self.kite.VARIETY_REGULAR, order_id=order_id)
