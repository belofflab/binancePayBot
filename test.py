from decimal import Decimal
from binance.pay.merchant import Merchant as BinancePayClient 
from uuid import uuid4 




API_KEY= 'udt23lduv4je0c1ly4zcgzzz8a8pyjzfurm3afoyw0i4x236ahjjjqom9meqsozk'

API_SECRET='ffkonns4uo7lcgpqce8phwbjzendzgzu7tlx1vnvkcn0dkird2l0sne3qjo0i7zw'

binancepay_client = BinancePayClient(key=API_KEY, secret=API_SECRET)

def uniqueId(): return str(uuid4()).replace('-', '')

toOrderId = uniqueId()

status = {
    "INITIAL", "PENDING", "PAID", "CANCELED", "ERROR", "REFUNDING", "REFUNDED", "EXPIRED"
}

def create_order(amount: Decimal, merchantTradeNo: str) -> dict:
    params = {
        "env": {"terminalType": "MINI_PROGRAM"},
        "merchantTradeNo": merchantTradeNo,
        "orderAmount": amount,
        "currency": "USDT",
        "goods": {
            "goodsType": "02",
            "goodsCategory": "Z000",
            "referenceGoodsId": merchantTradeNo,
            "goodsName": "Generated pdf file",
        },
    }


    return binancepay_client.new_order(params=params)

def get_order(merchantTradeNo: str) -> dict:
    return binancepay_client.get_order(merchantTradeNo=merchantTradeNo)


def close_order(merchantTradeNo) -> dict:
    return binancepay_client.cancel_order(merchantTradeNo=merchantTradeNo)


if __name__ == '__main__':

    orderId = "c7f232144b2445d786a3d483e492bb04"

    print(close_order(merchantTradeNo=orderId))