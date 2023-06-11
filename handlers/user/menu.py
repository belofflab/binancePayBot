import datetime
from decimal import Decimal
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext

from database import models
from keyboards.user import inline
from loader import bot, dp
from states.RefillState import Refill
from utils.payment import binancepay


async def get_or_create_user(user_id: int, username: str) -> models.User:
    user = await models.User.query.where(models.User.idx == user_id).gino.first()
    if user is not None:
        return user
    return await models.User.create(idx=user_id, username=username if username is not None else 'no username')


@dp.message_handler(commands='start')
async def start(message: Union[types.Message, types.CallbackQuery], **kwargs) -> None:
    await get_or_create_user(user_id=message.from_user.id, username=message.from_user.username)
    if isinstance(message, types.Message):
        await message.answer('Welcome to Meow Tech! \n\nAvailable menu: ', reply_markup=await inline.menu_keyboard())
    elif isinstance(message, types.CallbackQuery):
        await message.message.edit_text('Welcome to Meow Tech! \n\nAvailable menu: ', reply_markup=await inline.menu_keyboard())


async def start_payment_processing(message: types.Message,last_message_id, amount: Decimal):
    info_message = await bot.edit_message_text(text='Create a link for payment...',chat_id=message.from_user.id, message_id=last_message_id)
    merchantTradeNo=binancepay.uniqueId()
    new_order = await binancepay.create_order(amount=amount, merchantTradeNo=merchantTradeNo)
    refill_balance_markup = await inline.refill_balance_keyboard(payment_url=new_order['data']['checkoutUrl'], merchantTradeNo=merchantTradeNo)
    refill_message = await bot.edit_message_text(text='Waiting for payment...',chat_id=message.from_user.id, message_id=info_message.message_id, reply_markup=refill_balance_markup)
    await binancepay.wait_for_refill(
            merchantTradeNo=merchantTradeNo, 
            message_id=refill_message.message_id, 
            user_id=message.from_user.id
        )

async def to_profile(message_id, user_id) -> None:
    markup =await inline.profile_keyboard()
    c_user = await models.User.query.where(models.User.idx == user_id).gino.first()

    await bot.edit_message_text(text=
        f"""
Your profile: 
<b>ID:{c_user.idx}</b>
<b>Username: @{c_user.username}</b>

<b>Balance: </b> ${c_user.balance}

<b>Registration Date: </b> {datetime.datetime.strftime(c_user.created, "%Y-%m-%d")}

""", chat_id=user_id, message_id=message_id, reply_markup=markup)

@dp.callback_query_handler(lambda c:c.data == 'profile')
async def profile(callback: types.CallbackQuery) -> None:
    markup =await inline.profile_keyboard()
    c_user = await models.User.query.where(models.User.idx == callback.from_user.id).gino.first()

    await callback.message.edit_text(f"""
Your profile: 
<b>ID:{c_user.idx}</b>
<b>Username: @{c_user.username}</b>

<b>Balance: </b> ${c_user.balance}

<b>Registration Date: </b> {datetime.datetime.strftime(c_user.created, "%Y-%m-%d")}

""", reply_markup=markup)

@dp.callback_query_handler(lambda c:c.data == 'refill')
async def refill(callback: types.CallbackQuery, state: FSMContext) -> None:
    markup = await inline.refill_set_balance_keyboard()
    
    new_message = await callback.message.edit_text("Enter the recharge amount in $", reply_markup=markup)

    async with state.proxy() as data:
        data['last_message_id'] = new_message.message_id

    await Refill.amount.set()


@dp.message_handler(state=Refill.amount)
async def refill_set_amount(message: types.Message, state: FSMContext):
    amount = message.text 
    await message.delete()
    async with state.proxy() as data:
        last_message_id = data['last_message_id'] 
    try: 
        amount = int(amount)
        await state.finish()

        await start_payment_processing(
            message=message,
            last_message_id=last_message_id,
            amount=amount
        )
    except ValueError:
        markup =await inline.refill_set_balance_keyboard()
        new_message = await bot.edit_message_text(
                text="The amount entered is incorrect! \nInsert the deposit amount in $", 
                chat_id=message.from_user.id, 
                message_id=last_message_id, 
                reply_markup=markup
            )
        async with state.proxy() as data:
            data['last_message_id'] = new_message.message_id


@dp.callback_query_handler(lambda c: c.data.startswith('cancel_refill_set'), state=Refill.amount)
async def cancel_refill_set(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("Refills have been canceled!")
@dp.callback_query_handler(lambda c: c.data.startswith('cancel_payment'))
async def cancel_payment(callback: types.CallbackQuery):
    merchantTradeNo = callback.data.split('#')[-1]
    binancepay.close_order(merchantTradeNo=merchantTradeNo)

@dp.message_handler(commands='pay')
async def pay(message: types.Message) -> None:
    amount = message.text.split()[-1]

    await start_payment_processing(message=message, amount=amount)

async def list_deliveries(callback: types.CallbackQuery, **kwargs) -> None:
    markup = await inline.deliveries_keyboard()
    text = "Choose the right company"
    # if isinstance(callback, types.Message):
    #     await callback.answer_photo(photo=types.InputFile(BANNER),caption=text, reply_markup=markup)
    # elif isinstance(callback, types.CallbackQuery):
    #     await callback.message.edit_caption(caption=text,reply_markup=markup)
    await callback.message.edit_text(text=text, reply_markup=markup)

async def select_generation_method(callback: types.CallbackQuery, name: str, **kwargs) -> None:
    markup = await inline.delivery_method_keyboard(name)
    await callback.message.edit_text(f"<b>Selected Service: </b>{name}\n\nSelect a PDF generation method", reply_markup=markup)

async def show_delivery(callback: types.CallbackQuery, name: str, mode: str) -> None:
    markup = await inline.delivery_keyboard(name, mode)
    await callback.message.edit_text(f"<b>Selected service: </b>{name}\n<b>Selected mode:</b> {mode}", reply_markup=markup)

@dp.callback_query_handler(inline.delivery_cd.filter())
async def service_navigate(callback: types.CallbackQuery, callback_data: dict) -> None:
    level = callback_data.get("level")
    name = callback_data.get("name")
    mode = callback_data.get("mode")

    levels = {
        "0": start,
        "1": list_deliveries,
        "2": select_generation_method,
        "3": show_delivery
    }

    current_level_function = levels[level]

    await current_level_function(
        callback,
        name=name,
        mode=mode
    )