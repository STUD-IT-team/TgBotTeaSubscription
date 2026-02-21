from src.service_locator import get_repositories
from datetime import datetime

async def weekly_notification(logging, users, dp, bot, PaymentState):
    repos = await get_repositories() 
    
    logging.info("Запуск еженедельной проверки неоплативших...")
    for user_id, data in users.items():
        if data["status"] == "unpaid":
            try:
                state = dp.fsm.resolve_context(bot=bot, chat_id=user_id, user_id=user_id)
                await state.set_state(PaymentState.waiting_for_transaction)

                await bot.send_message(user_id,
                                " Напоминаем: у вас есть неоплаченный счет. Пожалуйста, отправьте номер транзакции.")
                await repos.user_repo.update_last_notification(user_id, last_notification_date=datetime.utcnow())
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение {user_id}: {e}")
