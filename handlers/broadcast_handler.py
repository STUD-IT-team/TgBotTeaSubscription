from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from src.repository.user_repo import UserRepository


class BroadcastState(StatesGroup):
    waiting_for_message = State()


async def broadcast_handler(router: Router, bot, ADMIN_ID, get_repositories):
    @router.message(Command("broadcast"))
    async def broadcast_command(message: Message, state: FSMContext):
        # Проверка, что команда от админа
        if message.from_user.id not in ADMIN_ID:
            await message.answer("У вас нет доступа к этой команде.")
            return

        await message.answer(
            "Введите сообщение для рассылки всем пользователям:\n"
            "(Отправьте текст, который будет отправлен всем пользователям)"
        )
        await state.set_state(BroadcastState.waiting_for_message)

    @router.message(BroadcastState.waiting_for_message)
    async def broadcast_message(message: Message, state: FSMContext):
        broadcast_text = message.text
        user_id = message.from_user.id

        # Проверка, что команда от админа
        if user_id not in ADMIN_ID:
            await message.answer("У вас нет доступа к этой команде.")
            await state.clear()
            return

        async_session_maker = await get_repositories()
        async with async_session_maker() as session:
            user_repo = UserRepository(session)
            all_users = await user_repo.get_all_users()

        # Исключаем админов из списка рассылки
        users_to_notify = [uid for uid in all_users if uid not in ADMIN_ID]

        success_count = 0
        failed_count = 0

        for tg_id in users_to_notify:
            try:
                await bot.send_message(chat_id=tg_id, text=broadcast_text)
                success_count += 1
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {tg_id}: {e}")
                failed_count += 1

        await message.answer(
            f"Рассылка завершена!\n"
            f"Успешно отправлено: {success_count}\n"
            f"Не удалось отправить: {failed_count}"
        )
        await state.clear()

    return router
