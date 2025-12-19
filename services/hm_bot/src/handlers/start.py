"""Start command handler."""

import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.api_client import api
from src.keyboards import main_menu_keyboard
from src.states import HMStates
from src import texts

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Handle /start command."""
    await state.clear()

    user = message.from_user
    telegram_id = user.id
    first_name = user.first_name or "Менеджер"
    last_name = user.last_name or ""

    # Create or get existing HM
    hm = await api.create_or_get_hm(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
    )

    if not hm:
        await message.answer(texts.ERROR_API)
        return

    # Save HM data to state
    await state.update_data(
        hm_id=hm["id"],
        hm_name=f"{first_name} {last_name}".strip(),
    )

    # Check if returning user (has vacancies)
    vacancies = await api.get_my_vacancies(hm["id"])

    if vacancies:
        text = texts.WELCOME_BACK.format(name=first_name)
    else:
        text = texts.WELCOME.format(name=first_name)

    await message.answer(text, reply_markup=main_menu_keyboard())
    await state.set_state(HMStates.in_menu)

