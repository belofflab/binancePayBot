import asyncio
import datetime

from loader import bot

from decimal import Decimal
from binance.pay.merchant import Merchant as BinancePayClient 
from uuid import uuid4 




API_KEY= 'udt23lduv4je0c1ly4zcgzzz8a8pyjzfurm3afoyw0i4x236ahjjjqom9meqsozk'

API_SECRET='ffkonns4uo7lcgpqce8phwbjzendzgzu7tlx1vnvkcn0dkird2l0sne3qjo0i7zw'

binancepay_client = BinancePayClient(key=API_KEY, secret=API_SECRET)

def uniqueId(): return str(uuid4()).replace('-', '')

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


async def notify_canceled(user_id, message_id, **kwargs):
    await bot.edit_message_text(chat_id=user_id, text='Пополнение было отменено.', message_id=message_id)


async def notify_expired(user_id, message_id, **kwargs):
    await bot.edit_message_text(chat_id=user_id, text='Время на пополнение истекло.', message_id=message_id)


async def notify_paid(user_id, message_id, **kwargs):
    await bot.edit_message_text(chat_id=user_id, text='Оплачено!', message_id=message_id)

async def notify_error(user_id, message_id, **kwargs):
    await bot.edit_message_text(chat_id=user_id, text='Произошла ошибка. Свяжитесь с поддержкой ', message_id=message_id)

async def notify_refunding(user_id, message_id, **kwargs):
    await bot.edit_message_text(chat_id=user_id, text='Произошла ошибка. Свяжитесь с поддержкой ', message_id=message_id)

async def notify_refunded(user_id, message_id, **kwargs):
    await bot.edit_message_text(chat_id=user_id, text='Произошла ошибка. Свяжитесь с поддержкой ', message_id=message_id)

async def notify(response, merchantTradeNo, user_id, message_id):
    status = {
        'PAID': notify_paid,
        'EXPIRED': notify_expired,
        'CANCELLED': notify_canceled,
        'ERROR': notify_error,
        'REFUNDING':notify_refunding,
        'REFUNDED':notify_refunded
    }
    await status[response](merchantTradeNo=merchantTradeNo,user_id=user_id, message_id=message_id)


async def wait_for_refill(merchantTradeNo, message_id: str, user_id: int):
        order = get_order(merchantTradeNo=merchantTradeNo)
        order_status = order['data']['status']
        # order_status = 'PAID'
        # close_order(merchantTradeNo=merchantTradeNo)
        while order_status == 'INITIAL':
            await asyncio.sleep(1)
            new_order_status = get_order(merchantTradeNo=merchantTradeNo)['data']['status']
            order_status = new_order_status
        await notify(order_status, merchantTradeNo, user_id, message_id)