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

from notifications.monthly_notification import monthly_notification
from notifications.weekly_notification import weekly_notification

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)
ADMIN_ID = [123456789, 987654321]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


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
                      day=1, hour=12, minute=0)

    scheduler.add_job(weekly_notification, 'cron',
                      args=[logging, users, dp, bot, PaymentState],
                      day=8, hour=12, minute=0)

    scheduler.start()
    print(1)
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    print(2)
    await dp.start_polling(bot)
    print(3)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")


async def test_telegram():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    try:
        me = await bot.get_me()
        print(f"Бот работает: @{me.username}")

        print("Удаление вебхука...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("Вебхук удален")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(test_telegram())