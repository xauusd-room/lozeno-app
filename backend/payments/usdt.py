from decimal import Decimal, InvalidOperation
from .base import PaymentProvider
class USDTPayment(PaymentProvider):
    name = "usdt"
    network = "TRON"
    token_symbol = "USDT"
    token_contract = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
    token_decimals = 6

    def create_payment(self, order_no, amount, product_name):
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Invalid USDT payment amount")

        if not value.is_finite() or value <= 0:
            raise ValueError("USDT payment amount must be positive")

        if value != value.quantize(Decimal("0.000001")):
            raise ValueError("USDT amount supports at most 6 decimal places")

        return {
            "provider": self.name,
            "order_no": str(order_no),
            "amount": format(value, ".6f"),
            "currency": self.token_symbol,
            "product_name": str(product_name),
            "status": "pending",
            "type": "crypto",
            "network": self.network,
            "token_standard": "TRC20",
            "token_contract": self.token_contract,
            "token_decimals": self.token_decimals,
            "receiving_address": None,
            "expires_at": None,
            "tx_hash": None,
            "verification": "pending",
        }
