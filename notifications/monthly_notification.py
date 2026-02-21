async def monthly_notification(logging, users, dp, bot, PaymentState):
    logging.info("Запуск ежемесячной рассылки...")
    for user_id, data in users.items():
        users[user_id]["status"] = "unpaid"

        try:
            state = dp.fsm.resolve_context(bot=bot, chat_id=user_id, user_id=user_id)
            await state.set_state(PaymentState.waiting_for_transaction)

            await bot.send_message(user_id,
                                   " Пришло время ежемесячной оплаты! Пожалуйста, оплатите и отправьте **номер транзакции** ответным сообщением.")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение {user_id}: {e}")
