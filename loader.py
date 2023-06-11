from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from binance.pay.merchant import Merchant as BinancePayClient

from data.config import BINANCEPAY_KEY, BINANCEPAY_SECRET, BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
binancepay_client = BinancePayClient(key=BINANCEPAY_KEY, secret=BINANCEPAY_SECRET)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage) 

