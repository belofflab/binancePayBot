from aiogram.dispatcher.filters.state import State, StatesGroup


class Refill(StatesGroup):
    amount = State()