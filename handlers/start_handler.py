# start_handler.py
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

router = Router()

async def start_handler(router: Router, bot, users, get_repositories, PaymentState, dp):
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(f"Привет, {message.from_user.first_name}!")
        user_id = message.from_user.id
        repos = await get_repositories() 
        await repos.user_repo.add(user_id)

        state = dp.fsm.resolve_context(bot=bot, chat_id=user_id, user_id=user_id)
        await state.set_state(PaymentState.waiting_for_transaction)

        users[user_id] = {
            "username": message.from_user.username or str(user_id),
            "status": "unpaid"
        }
        print(users)
        int price = await get_price()

        await message.answer(
            f"Добро пожаловать! Оплатите взнос {price} рублей за этот месяц."
        )

    return router