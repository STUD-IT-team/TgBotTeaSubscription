import asyncio
import logging
import os

from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.types import Message
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from handlers.start_handler import start_handler
from handlers.admin_decision_handler import admin_handler
from handlers.transaction_handler import transaction_handler
from handlers.change_handler import change_handler

from notifications.monthly_notification import monthly_notification
from notifications.weekly_notification import weekly_notification
from src.service_locator import get_repositories



load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)
ADMIN_ID = [1476675808]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


users = {} #{user_id: {"username": str, "status": "unpaid" | "pending" | "paid"}}

admin_messages = {} #{"admin_id": int, "message_id": int}

class AdminConfirmCallback(CallbackData, prefix="admin_tx"):
    action: str
    user_id: int
    tx_number: str
    price: int

class ChangeConfirmCallback(CallbackData, prefix="change"):
    action: str  # "approve" или "reject"
    user_id: int
    amount: int

class PaymentState(StatesGroup):
    waiting_for_transaction = State()
    waiting_for_confirmation = State()


async def main():
    logging.basicConfig(level=logging.INFO)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(monthly_notification, 'cron',
                      args=[logging, users, dp, bot, PaymentState],
                      day=1, hour=12)

    scheduler.add_job(weekly_notification, 'interval',
                      args=[logging, users, dp, bot, PaymentState],
                       days=7)

    scheduler.start()

    await start_handler(router, bot, users, get_repositories, PaymentState, dp)
    await admin_handler(router, bot, admin_messages, AdminConfirmCallback, ADMIN_ID, get_repositories)
    await transaction_handler(router, bot, admin_messages, AdminConfirmCallback, ADMIN_ID, PaymentState, get_repositories)
    await change_handler(router, bot, admin_messages, PaymentState, ChangeConfirmCallback, ADMIN_ID, get_repositories)
    dp.include_router(router)


    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="change", description="Изменить взнос")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())