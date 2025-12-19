"""Main menu handler."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.keyboards import main_menu_keyboard
from src.states import HMStates
from src import texts

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Return to main menu."""
    await callback.answer()

    data = await state.get_data()
    parts = data.get("hm_name", "").split()
    name = parts[0] if parts else "друг"

    await callback.message.edit_text(
        texts.WELCOME_BACK.format(name=name),
        reply_markup=main_menu_keyboard(),
    )
    await state.set_state(HMStates.in_menu)


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Cancel current action and return to menu."""
    await callback.answer("Отменено")
    await back_to_menu(callback, state)

