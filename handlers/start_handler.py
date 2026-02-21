from aiogram.filters import CommandStart
from aiogram.types import Message
import main
from src.service_locator import get_repositories

@main.router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    repos = await get_repositories() 
    await repos.user_repo.add(user_id)

    main.users[user_id] = {
        "username": message.from_user.username or str(user_id),
        "status": "unpaid"
    }
    await message.answer("Добро пожаловать! Я буду присылать вам напоминания об оплате.")