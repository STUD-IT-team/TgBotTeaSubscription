from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from typing import Dict, List

async def change_handler(router: Router, bot, admin_messages, PaymentState, ChangeConfirmCallback, ADMIN_ID: List[int]):
    @router.message(Command("change"))
    async def change_command(message: Message, state: FSMContext):
        args = message.text.split()
        if len(args) != 2:
            await message.answer(" Неправильный формат команды. Используйте: /change <сумма>")
            return

        try:
            amount = int(args[1])

            if amount <= 0:
                await message.answer(" Сумма должна быть положительным числом")
                return

            user_id = message.from_user.id
            username = message.from_user.username or str(user_id)

            builder = InlineKeyboardBuilder()
            builder.button(
                text=" Подтвердить",
                callback_data=ChangeConfirmCallback(action="approve", user_id=user_id, amount=amount)
            )
            builder.button(
                text=" Отклонить",
                callback_data=ChangeConfirmCallback(action="reject", user_id=user_id, amount=amount)
            )
            builder.adjust(2)

            admin_text = (
                f" Запрос на изменение цены\n"
                f" Пользователь: @{username}\n"
                f" ID: {user_id}\n"
                f" Новая цена: {amount} рублей"
            )

            request_key = f"{user_id}_{amount}_{message.message_id}"
            admin_messages[request_key] = []

            for admin_id in ADMIN_ID:
                try:
                    msg = await bot.send_message(
                        chat_id=admin_id,
                        text=admin_text,
                        reply_markup=builder.as_markup()
                    )
                    admin_messages[request_key].append({
                        "admin_id": admin_id,
                        "message_id": msg.message_id
                    })
                except Exception as e:
                    print(f"Ошибка отправки админу {admin_id}: {e}")

            await state.update_data(
                request_key=request_key,
                amount=amount,
                user_id=user_id
            )

            await message.answer(
                f"Запрос на изменение цены до {amount} рублей отправлен администратору на проверку.\n"
                f"Ожидайте подтверждения."
            )

            await state.set_state(PaymentState.waiting_for_confirmation)

        except ValueError:
            await message.answer(" Сумма должна быть числом")
            return

    @router.callback_query(ChangeConfirmCallback.filter())
    async def change_confirm_callback(
            callback: CallbackQuery,
            callback_data: ChangeConfirmCallback,
    ):
        action = callback_data.action
        user_id = callback_data.user_id
        amount = callback_data.amount

        request_key = f"{user_id}_{amount}_{callback.message.message_id - 1}"

        if action == "approve":
            change_price()

            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"Ваш запрос на изменение цены до {amount} рублей был одобрен!"
                )
            except Exception as e:
                print(f"Ошибка уведомления пользователя {user_id}: {e}")

            await callback.message.edit_text(
                f"{callback.message.text}\n\nЗапрос подтвержден администратором"
            )

        elif action == "reject":
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"Ваш запрос на изменение цены до {amount} рублей был отклонен."
                )
            except Exception as e:
                print(f"Ошибка уведомления пользователя {user_id}: {e}")

            await callback.message.edit_text(
                f"{callback.message.text}\n\n Запрос отклонен администратором"
            )

        await callback.message.edit_reply_markup(reply_markup=None)

        if request_key in admin_messages:
            del admin_messages[request_key]

        await callback.answer()

    return router