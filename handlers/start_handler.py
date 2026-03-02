# start_handler.py
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from src.repository.user_repo import UserRepository

router = Router()

async def start_handler(router: Router, bot, users, get_repositories, PaymentState, dp):
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(f"Привет, {message.from_user.first_name}!")
        user_id = message.from_user.id
        async_session_maker = await get_repositories()
        async with async_session_maker() as session:
            user_repo = UserRepository(session)
            await user_repo.add(user_id)

            state = dp.fsm.resolve_context(bot=bot, chat_id=user_id, user_id=user_id)
            await state.set_state(PaymentState.waiting_for_transaction)

            users[user_id] = {
                "username": message.from_user.username or str(user_id),
                "status": "unpaid"
            }
            price = await user_repo.get_by_tg_id(user_id)

            await message.answer(
                f"Добро пожаловать! Оплатите взнос {price} рублей за этот месяц и отправьте скриншот чека."
            )

    return router