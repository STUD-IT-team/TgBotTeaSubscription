from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from aiogram import Router
from src.repository.user_repo import UserRepository
import time


async def transaction_handler(router: Router, bot, admin_messages, AdminConfirmCallback, ADMIN_ID, PaymentState, get_repositories):
    @router.message(StateFilter(PaymentState.waiting_for_transaction))
    async def transaction_handler(message: Message, state: FSMContext):
        # Проверяем, что прислоно фото (скриншот чека)
        if not message.photo:
            await message.answer("Пожалуйста, отправьте скриншот чека об оплате.")
            return

        # Получаем фото
        photo = message.photo[-1]  # Берем самое большое фото
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        # Генерируем короткий уникальный ключ для этого чека (используем timestamp)
        receipt_id = f"{int(time.time())}_{user_id}"
        
        async_session_maker = await get_repositories()
        async with async_session_maker() as session:
            user_repo = UserRepository(session)
            price = await user_repo.get_by_tg_id(user_id)

            builder = InlineKeyboardBuilder()
            builder.button(text="Подтвердить",
                        callback_data=AdminConfirmCallback(action="approve", user_id=user_id, tx_number=receipt_id, price=price))
            builder.button(text="Отклонить",
                        callback_data=AdminConfirmCallback(action="reject", user_id=user_id, tx_number=receipt_id, price=price))
            builder.adjust(2)
            
            admin_text = f"Пользователь: @{username}\nID: {user_id}\nВзнос: {price}\nСкриншот чека:"

            admin_messages[receipt_id] = []

            for admin_id in ADMIN_ID:
                try:
                    msg = await bot.send_photo(
                        chat_id=admin_id,
                        photo=photo.file_id,
                        caption=admin_text,
                        reply_markup=builder.as_markup()
                    )
                    admin_messages[receipt_id].append({"admin_id": admin_id, "message_id": msg.message_id})
                except Exception as e:
                    print(f"Не удалось отправить чек админу {admin_id}: {e}")

            await message.answer("Чек отправлен администратору на проверку.")
            await state.clear()

    return router
