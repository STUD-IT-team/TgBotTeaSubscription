from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router


class AdminPanelCallback(CallbackData, prefix="admin_panel"):
    action: str


async def admin_panel_handler(router: Router, bot, ADMIN_ID, get_repositories):
    @router.message(Command("admin"))
    async def admin_panel(message: Message):
        # Проверка, что команда от админа
        if message.from_user.id not in ADMIN_ID:
            await message.answer("У вас нет доступа к этой команде.")
            return

        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Рассылка", callback_data=AdminPanelCallback(action="broadcast"))
        builder.adjust(1)

        await message.answer(
            "Панель администратора:",
            reply_markup=builder.as_markup()
        )

    @router.callback_query(AdminPanelCallback.filter())
    async def admin_panel_callback(callback: CallbackQuery, callback_data: AdminPanelCallback, state: FSMContext):
        if callback.from_user.id not in ADMIN_ID:
            await callback.answer("У вас нет доступа", show_alert=True)
            return

        if callback_data.action == "broadcast":
            await callback.message.answer(
                "Введите сообщение для рассылки всем пользователям:\n"
                "(Отправьте текст, который будет отправлен всем пользователям)"
            )
            from handlers.broadcast_handler import BroadcastState
            await state.set_state(BroadcastState.waiting_for_message)

        await callback.answer()

    return router
