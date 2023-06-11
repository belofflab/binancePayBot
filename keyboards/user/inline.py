from database import models
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

delivery_cd = CallbackData("show_delivery", "level", "name")

def make_delivery_cd(level, name="0"):
    return delivery_cd.new(level=level, name=name)

async def refill_balance_keyboard(payment_url, merchantTradeNo):

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text='Пополнить',
            url=payment_url
        ),
        InlineKeyboardButton(
            text='Отмена',
            callback_data=f'cancel_payment#{merchantTradeNo}'
        )
    )

    return markup

async def refill_set_balance_keyboard():

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel_refill_set'
        )
    )

    return markup

async def menu_keyboard():
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        {'text': 'Сгенерировать PDF!', 'callback_data': make_delivery_cd(CURRENT_LEVEL + 1)},
        {'text': 'Профиль', 'callback_data': 'profile'},
        {'text': 'Поддержка', 'url': 'https://t.me/meow_tech'},
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
        {'text': 'Пополнить', 'callback_data': 'refill'},
        {'text': 'Назад', 'callback_data': make_delivery_cd(level=0)}
    ]
    for button in buttons:
        markup.insert(InlineKeyboardButton(**button))

    return markup

async def deliveries_keyboard():
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=3)
    deliveries = [
        {'text': 'usp', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name="usd")},
        {'text': 'usps', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name="usds")},
        {'text': 'fedex', 'callback_data': make_delivery_cd(level=CURRENT_LEVEL + 1, name="fedex")}
    ]

    for delivery in deliveries:
        markup.insert(InlineKeyboardButton(**delivery))

    markup.row(
        InlineKeyboardButton(
        text='Назад',
        callback_data=make_delivery_cd(CURRENT_LEVEL - 1)
        )
    )

    return markup

async def delivery_keyboard():
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
        text='Назад',
        callback_data=make_delivery_cd(CURRENT_LEVEL - 1)
        )
    )

    return markup