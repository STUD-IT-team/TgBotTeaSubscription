from aiogram.filters import Command
from aiogram.types import Message
import main
from src.service_locator import get_repositories

@main.router.message(Command("star"))
async def start_handler(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")
    user_id = message.from_user.id
    print(4)
    repos = await get_repositories() 
    await repos.user_repo.add(user_id)

    main.users[user_id] = {
        "username": message.from_user.username or str(user_id),
        "status": "unpaid"
    }
    await message.answer("Добро пожаловать! Я буду присылать вам напоминания об оплате.")