import asyncio
from decimal import Decimal
from uuid import uuid4

from database import models
from handlers.user import menu
from loader import binancepay_client, bot

from requests.exceptions import ConnectTimeout

def uniqueId(): return str(uuid4()).replace('-', '')


async def profile_redirect(redirect_message, user_id, message_id):
    await bot.edit_message_text(
            chat_id=user_id,
            text=redirect_message + "\n\nRedirecting to a personal account...", 
            message_id=message_id
        )
    await asyncio.sleep(1)
    await menu.to_profile(message_id=message_id, user_id=user_id)


async def create_order(amount: Decimal, merchantTradeNo: str) -> dict:
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

    try:
        new_order = binancepay_client.new_order(params=params)
    except ConnectTimeout:
        await asyncio.sleep(0.3)
        new_order = create_order(amount=amount, merchantTradeNo=merchantTradeNo)

    return new_order

def get_order(merchantTradeNo: str) -> dict:
    return binancepay_client.get_order(merchantTradeNo=merchantTradeNo)


def close_order(merchantTradeNo) -> dict:
    return binancepay_client.cancel_order(merchantTradeNo=merchantTradeNo)


async def notify_canceled(user_id, message_id, **kwargs):
    await profile_redirect(
        redirect_message="The refill has been canceled",
        user_id=user_id,
        message_id=message_id
    )


async def notify_expired(user_id, message_id, **kwargs):
    await profile_redirect(
        redirect_message="Refill time has expired",
        user_id=user_id,
        message_id=message_id
    )


async def notify_paid(user_id, message_id, merchantTradeNo):
    order = get_order(merchantTradeNo=merchantTradeNo)
    await models.User.update.values(
            balance=models.User.balance + order['data']['orderAmount']
        ).where(models.User.idx == user_id).gino.status()
    await profile_redirect(
        redirect_message="Payment was successful",
        user_id=user_id,
        message_id=message_id
    )


async def notify_error(user_id, message_id, **kwargs):
    await profile_redirect(
        redirect_message="Something went wrong. Contact support!",
        user_id=user_id,
        message_id=message_id
    )

async def notify_refunding(user_id, message_id, **kwargs):
    await profile_redirect(
        redirect_message="Something went wrong. Contact support!",
        user_id=user_id,
        message_id=message_id
    )

async def notify_refunded(user_id, message_id, **kwargs):
    await profile_redirect(
        redirect_message="Something went wrong. Contact support!",
        user_id=user_id,
        message_id=message_id
    )

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