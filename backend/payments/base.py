class PaymentProvider:
    name="unknown"

    def create_payment(self,order_no,amount,product_name):
        return {
            "provider":self.name,
            "order_no":order_no,
            "amount":amount,
            "product_name":product_name,
            "status":"pending"
        }

    def query_payment(self,order_no):
        return {"order_no":order_no,"status":"pending"}