# start_handler.py
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from src.service_locator import get_repositories

router = Router()

# users — словарь с данными пользователей, передается из main
# PaymentState — класс состояния FSM, передается из main
def start_handler(users: dict, PaymentState):
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(f"Привет, {message.from_user.first_name}!")
        user_id = message.from_user.id
        repos = await get_repositories() 
        await repos.user_repo.add(user_id)

        users[user_id] = {
            "username": message.from_user.username or str(user_id),
            "status": "unpaid"
        }
        print(users)
        await message.answer(
            "Добро пожаловать! Я буду присылать вам напоминания об оплате."
        )

    return router