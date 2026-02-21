import asyncio
import logging
import os

from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from handlers.start_handler import start_handler

from notifications.monthly_notification import monthly_notification
from notifications.weekly_notification import weekly_notification
from src.service_locator import get_repositories

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)
ADMIN_ID = [123456789, 987654321]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# router = Router()


users = {} #{user_id: {"username": str, "status": "unpaid" | "pending" | "paid"}}

admin_messages = {} #{"admin_id": int, "message_id": int}

class AdminConfirmCallback(CallbackData, prefix="admin_tx"):
    action: str
    user_id: int
    tx_number: str


class PaymentState(StatesGroup):
    waiting_for_transaction = State()


async def main():
    logging.basicConfig(level=logging.INFO)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(monthly_notification, 'cron',
                      args=[logging, users, dp, bot, PaymentState],
                      day=21, hour=16, minute=45)

    scheduler.add_job(weekly_notification, 'interval',
                      args=[logging, users, dp, bot, PaymentState],
                       days=7)

    scheduler.start()
    start_router = start_handler(users, PaymentState)
    dp.include_router(start_router)

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)
    print(3)

# @router.message(Command("start"))
# async def cmd_start(message: Message):
#     await message.answer(f"Привет, {message.from_user.first_name}!")
#     user_id = message.from_user.id
#     repos = await get_repositories() 
#     await repos.user_repo.add(user_id)

#     users[user_id] = {
#         "username": message.from_user.username or str(user_id),
#         "status": "unpaid"
#     }
#     print(users)
#     await message.answer("Добро пожаловать! Я буду присылать вам напоминания об оплате.")

if __name__ == "__main__":
    asyncio.run(main())