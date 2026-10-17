from .wechat import WeChatPayment
from .alipay import AliPayPayment
from .usdt import USDTPayment

providers={
    "wechat":WeChatPayment(),
    "alipay":AliPayPayment(),
    "usdt":USDTPayment()
}

def get_payment_provider(method):
    provider=providers.get(method)
    if not provider:
        raise ValueError(f"不支持的支付方式: {method}")
    return provider