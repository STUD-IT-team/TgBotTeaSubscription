from aiogram.types import CallbackQuery
from aiogram import Router
from datetime import datetime
from src.repository.transact_repo import TransactionRepository

router = Router()

async def admin_handler(router: Router, bot, admin_messages, AdminConfirmCallback, ADMIN_ID, get_repositories):
    @router.callback_query(AdminConfirmCallback.filter())
    async def admin_decision_handler(callback: CallbackQuery, callback_data: AdminConfirmCallback):
        async_session_maker = await get_repositories()
        async with async_session_maker() as session:
            transaction_repo = TransactionRepository(session)

            user_id = callback_data.user_id
            action = callback_data.action
            receipt_id = callback_data.tx_number  # Теперь это receipt_id, а не номер транзакции
            price = callback_data.price
            admin_id = callback.from_user.id

            if action == "approve":
                await transaction_repo.add(user_id, receipt_id, price, datetime.now(), admin_id)
                await bot.send_message(user_id, "Ваша оплата успешно подтверждена!")
                await callback.message.edit_text(callback.message.text + "\n\n✅ ПОДТВЕРЖДЕНО")
                # Удаляем сообщение админа после подтверждения
                try:
                    await bot.delete_message(chat_id=admin_id, message_id=callback.message.message_id)
                except Exception as e:
                    print(f"Не удалось удалить сообщение: {e}")

            elif action == "reject":
                await bot.send_message(user_id, "Ваша транзакция отклонена. Пожалуйста, проверьте данные и отправьте чек снова.")
                await callback.message.edit_text(callback.message.text + "\n\n❌ ОТКЛОНЕНО")
                # Удаляем сообщение админа после отклонения
                try:
                    await bot.delete_message(chat_id=admin_id, message_id=callback.message.message_id)
                except Exception as e:
                    print(f"Не удалось удалить сообщение: {e}")

            # удаляем сообщения у других админов
            if receipt_id in admin_messages:
                for msg_data in admin_messages[receipt_id]:
                    if msg_data["admin_id"] != admin_id:
                        try:
                            await bot.delete_message(chat_id=msg_data["admin_id"], message_id=msg_data["message_id"])
                        except Exception as e:
                            print(f"Не удалось удалить сообщение у админа {msg_data['admin_id']}: {e}")
                del admin_messages[receipt_id]

            await callback.answer()
