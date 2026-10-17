from .base import PaymentProvider

class AliPayPayment(PaymentProvider):
    name="alipay"

    def create_payment(self,order_no,amount,product_name):
        return {
            "provider":"alipay",
            "order_no":order_no,
            "amount":amount,
            "product_name":product_name,
            "status":"pending",
            "type":"qr"
        }