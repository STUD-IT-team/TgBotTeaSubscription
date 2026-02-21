from src.service_locator import get_repositories
from datetime import datetime

async def monthly_notification(logging, users, dp, bot, PaymentState):
    repos = await get_repositories() 
    logging.info("Запуск ежемесячной рассылки...")
    for user_id, data in users.items():
        users[user_id]["status"] = "unpaid"

        try:
            state = dp.fsm.resolve_context(bot=bot, chat_id=user_id, user_id=user_id)
            await state.set_state(PaymentState.waiting_for_transaction)
            int price = await get_price()
            await bot.send_message(user_id,
                                   f" Пришло время ежемесячной оплаты! Пожалуйста, оплатите {price} рублей и отправьте номер транзакции.")
            await repos.user_repo.update_last_notification(user_id, last_notification_date=datetime.utcnow())
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение {user_id}: {e}")
