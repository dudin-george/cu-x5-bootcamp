"""Candidate selection handlers (Tinder mode)."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.api_client import api
from src.keyboards import (
    candidate_actions_keyboard,
    vacancy_detail_keyboard,
    back_to_menu_keyboard,
)
from src.states import HMStates
from src import texts

logger = logging.getLogger(__name__)
router = Router()


async def show_next_candidate(
    message: types.Message,
    state: FSMContext,
    vacancy_id: int,
    edit: bool = True,
) -> None:
    """Show next candidate for vacancy."""
    candidate = await api.get_next_candidate(vacancy_id)

    if not candidate:
        # No more candidates
        text = texts.NO_MORE_CANDIDATES
        keyboard = vacancy_detail_keyboard(vacancy_id)

        if edit:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)

        await state.set_state(HMStates.viewing_vacancy)
        return

    candidate_id = candidate["id"]

    # Build candidate card
    text = texts.CANDIDATE_CARD.format(
        name=candidate.get("name", "—"),
        surname=candidate.get("surname", "—"),
        university=candidate.get("university") or "Не указан",
        course=candidate.get("course") or "—",
        priority=candidate.get("priority1") or "Не указано",
        tech_stack=candidate.get("tech_stack") or "Не указан",
        city=candidate.get("city") or "Не указан",
        hours=candidate.get("employment_hours") or "Не указано",
        email=candidate.get("email") or "—",
        phone=candidate.get("phone") or "—",
    )

    await state.update_data(current_candidate_id=candidate_id)

    keyboard = candidate_actions_keyboard(vacancy_id, candidate_id)

    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)

    await state.set_state(HMStates.picking_candidate)


@router.callback_query(F.data.startswith("pick_"))
async def start_picking(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Start picking candidates for vacancy."""
    await callback.answer()

    vacancy_id = int(callback.data.split("_")[1])
    await state.update_data(current_vacancy_id=vacancy_id)

    await show_next_candidate(callback.message, state, vacancy_id)


@router.callback_query(F.data.startswith("invite_"))
async def invite_candidate(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Invite candidate (select)."""
    await callback.answer("✅ Приглашён!")

    parts = callback.data.split("_")
    vacancy_id = int(parts[1])
    candidate_id = parts[2]

    result = await api.select_candidate(vacancy_id, candidate_id)

    if not result:
        await callback.message.edit_text(
            texts.ERROR_API,
            reply_markup=back_to_menu_keyboard(),
        )
        return

    # Show brief confirmation then next candidate
    await callback.message.edit_text(texts.CANDIDATE_INVITED.format(name="Кандидат"))

    # Small delay would be nice here, but let's just show next
    await show_next_candidate(callback.message, state, vacancy_id, edit=False)


@router.callback_query(F.data.startswith("skip_"))
async def skip_candidate(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Skip candidate."""
    await callback.answer("⏭️ Пропущено")

    parts = callback.data.split("_")
    vacancy_id = int(parts[1])
    candidate_id = parts[2]

    result = await api.skip_candidate(vacancy_id, candidate_id)

    if not result:
        await callback.message.edit_text(
            texts.ERROR_API,
            reply_markup=back_to_menu_keyboard(),
        )
        return

    await show_next_candidate(callback.message, state, vacancy_id)


@router.callback_query(F.data.startswith("reject_"))
async def reject_candidate(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Reject candidate."""
    await callback.answer("❌ Отклонён")

    parts = callback.data.split("_")
    vacancy_id = int(parts[1])
    candidate_id = parts[2]

    result = await api.reject_candidate(vacancy_id, candidate_id)

    if not result:
        await callback.message.edit_text(
            texts.ERROR_API,
            reply_markup=back_to_menu_keyboard(),
        )
        return

    await show_next_candidate(callback.message, state, vacancy_id)

