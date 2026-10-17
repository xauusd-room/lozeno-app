from .base import PaymentProvider

class USDTPayment(PaymentProvider):
    name="usdt"

    def create_payment(self,order_no,amount,product_name):
        return {
            "provider":"usdt",
            "order_no":order_no,
            "amount":amount,
            "product_name":product_name,
            "status":"pending",
            "type":"crypto",
            "network":"TRC20"
        }