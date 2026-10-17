from .base import PaymentProvider

class WeChatPayment(PaymentProvider):
    name="wechat"

    def create_payment(self,order_no,amount,product_name):
        return {
            "provider":"wechat",
            "order_no":order_no,
            "amount":amount,
            "product_name":product_name,
            "status":"pending",
            "type":"qr"
        }