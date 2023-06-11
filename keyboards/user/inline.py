from database import models
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

delivery_cd = CallbackData("show_delivery", "level", "name", "mode")

def make_delivery_cd(level, name="0", mode="0"):
    return delivery_cd.new(level=level, name=name, mode=mode)

async def refill_balance_keyboard(payment_url, merchantTradeNo):

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text='Refill',
            url=payment_url
        ),
        InlineKeyboardButton(
            text='Cancel',
            callback_data=f'cancel_payment#{merchantTradeNo}'
        )
    )

    return markup

async def refill_set_balance_keyboard():

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text='Cancel',
            callback_data='cancel_refill_set'
        )
    )

    return markup

async def menu_keyboard():
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        {'text': 'Generate PDF!', 'callback_data': make_delivery_cd(CURRENT_LEVEL + 1)},
        {'text': 'Profile', 'callback_data': 'profile'},
        {'text': 'Support', 'url': 'https://t.me/meow_tech'},
    ]
    for idx, button in enumerate(buttons):
        if idx == 1:
            markup.row(InlineKeyboardButton(**button))
        else:
            markup.insert(InlineKeyboardButton(**button))

    return markup


async def profile_keyboard():

    markup = InlineKeyboardMarkup()
    buttons = [
        {'text': 'Refill', 'callback_data': 'refill'},
        {'text': 'Back', 'callback_data': make_delivery_cd(level=0)}
    ]
    for button in buttons:
        markup.insert(InlineKeyboardButton(**button))

    return markup

async def deliveries_keyboard():
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=3)
    deliveries = [
        {'text': 'Usp', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name="usp")},
        {'text': 'Usps', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name="usps")},
        {'text': 'Fedex', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name="fedex")}
    ]

    for delivery in deliveries:
        markup.insert(InlineKeyboardButton(**delivery))

    markup.row(
        InlineKeyboardButton(
            text='Back',
            callback_data=make_delivery_cd(CURRENT_LEVEL - 1)
        )
    )

    return markup

async def delivery_method_keyboard(name):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = [
        {'text': 'Auto', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name=name, mode="auto")},
        {'text': 'Manual', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name=name, mode="manual")}
    ]

    for button in buttons:
        markup.insert(
            InlineKeyboardButton(**button)
        )

    markup.row(
        InlineKeyboardButton(
        text='Back',
        callback_data=make_delivery_cd(CURRENT_LEVEL - 1)
        )
    )

    return markup

async def delivery_keyboard(name, mode):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=2)

    markup.row(
        InlineKeyboardButton(
        text='Back',
        callback_data=make_delivery_cd(CURRENT_LEVEL - 1, name=name)
        )
    )

    return markup