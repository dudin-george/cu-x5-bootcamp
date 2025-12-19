"""Vacancy creation and viewing handlers."""

import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.api_client import api
from src.keyboards import (
    tracks_keyboard,
    confirm_vacancy_keyboard,
    vacancies_keyboard,
    vacancy_detail_keyboard,
    main_menu_keyboard,
    cancel_keyboard,
)
from src.states import HMStates
from src import texts

logger = logging.getLogger(__name__)
router = Router()


# =============================================================================
# Create Vacancy Flow
# =============================================================================


@router.callback_query(F.data == "create_vacancy")
async def start_create_vacancy(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Start vacancy creation - select track."""
    await callback.answer()

    tracks = await api.get_tracks(active_only=True)

    if not tracks:
        await callback.message.edit_text(
            texts.ERROR_NO_TRACKS,
            reply_markup=main_menu_keyboard(),
        )
        return

    await callback.message.edit_text(
        texts.SELECT_TRACK,
        reply_markup=tracks_keyboard(tracks),
    )
    await state.set_state(HMStates.selecting_track)


@router.callback_query(HMStates.selecting_track, F.data.startswith("track_"))
async def track_selected(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle track selection."""
    await callback.answer()

    track_id = int(callback.data.split("_")[1])

    # Get track name
    track = await api.get_track_by_id(track_id)
    track_name = track["name"] if track else f"Трек {track_id}"

    await state.update_data(
        track_id=track_id,
        track_name=track_name,
    )

    await callback.message.edit_text(
        texts.ENTER_DESCRIPTION.format(track=track_name),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(HMStates.entering_description)


@router.message(HMStates.entering_description)
async def description_entered(message: types.Message, state: FSMContext) -> None:
    """Handle vacancy description input."""
    description = message.text.strip()

    if len(description) < 10:
        await message.answer(
            "Описание слишком короткое. Напиши подробнее (минимум 10 символов):",
            reply_markup=cancel_keyboard(),
        )
        return

    data = await state.get_data()
    hm_id = data.get("hm_id")
    track_id = data.get("track_id")
    track_name = data.get("track_name")

    # Create vacancy (DRAFT)
    vacancy = await api.create_vacancy(
        track_id=track_id,
        hiring_manager_id=hm_id,
        description=description,
    )

    if not vacancy:
        await message.answer(texts.ERROR_API, reply_markup=main_menu_keyboard())
        await state.set_state(HMStates.in_menu)
        return

    await state.update_data(
        draft_vacancy_id=vacancy["id"],
        description=description,
    )

    await message.answer(
        texts.CONFIRM_VACANCY.format(
            track=track_name,
            description=description,
        ),
        reply_markup=confirm_vacancy_keyboard(),
    )
    await state.set_state(HMStates.confirming_vacancy)


@router.callback_query(HMStates.confirming_vacancy, F.data == "publish_vacancy")
async def publish_vacancy(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Activate vacancy (DRAFT -> ACTIVE)."""
    await callback.answer()

    data = await state.get_data()
    vacancy_id = data.get("draft_vacancy_id")

    result = await api.activate_vacancy(vacancy_id)

    if not result:
        await callback.message.edit_text(
            texts.ERROR_API,
            reply_markup=main_menu_keyboard(),
        )
        await state.set_state(HMStates.in_menu)
        return

    await callback.message.edit_text(
        texts.VACANCY_CREATED,
        reply_markup=main_menu_keyboard(),
    )
    await state.set_state(HMStates.in_menu)


@router.callback_query(HMStates.confirming_vacancy, F.data == "edit_description")
async def edit_description(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Go back to description editing."""
    await callback.answer()

    data = await state.get_data()
    track_name = data.get("track_name")

    await callback.message.edit_text(
        texts.ENTER_DESCRIPTION.format(track=track_name),
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(HMStates.entering_description)


@router.callback_query(HMStates.confirming_vacancy, F.data == "abort_vacancy")
async def abort_vacancy(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Abort vacancy creation."""
    await callback.answer()

    data = await state.get_data()
    vacancy_id = data.get("draft_vacancy_id")

    if vacancy_id:
        await api.abort_vacancy(vacancy_id)

    await callback.message.edit_text(
        texts.VACANCY_ABORTED,
        reply_markup=main_menu_keyboard(),
    )
    await state.set_state(HMStates.in_menu)


# =============================================================================
# View Vacancies
# =============================================================================


@router.callback_query(F.data == "my_vacancies")
async def show_my_vacancies(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Show list of HM's vacancies."""
    await callback.answer()

    data = await state.get_data()
    hm_id = data.get("hm_id")

    if not hm_id:
        await callback.message.edit_text(
            texts.ERROR_API,
            reply_markup=main_menu_keyboard(),
        )
        return

    vacancies = await api.get_my_vacancies(hm_id, status_filter="ACTIVE")

    if not vacancies:
        await callback.message.edit_text(
            texts.NO_VACANCIES,
            reply_markup=main_menu_keyboard(),
        )
        return

    await callback.message.edit_text(
        texts.MY_VACANCIES,
        reply_markup=vacancies_keyboard(vacancies),
    )
    await state.set_state(HMStates.viewing_vacancies)


@router.callback_query(F.data.startswith("vacancy_"))
async def show_vacancy_detail(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Show vacancy details."""
    await callback.answer()

    vacancy_id = int(callback.data.split("_")[1])

    # Get vacancy details
    vacancy = await api.get_vacancy(vacancy_id)
    if not vacancy:
        await callback.message.edit_text(
            texts.ERROR_API,
            reply_markup=main_menu_keyboard(),
        )
        return

    # Get stats
    stats = await api.get_vacancy_stats(vacancy_id)

    # Get track name
    track = await api.get_track_by_id(vacancy["track_id"])
    track_name = track["name"] if track else "—"

    # Status display
    status_map = {
        "DRAFT": "📝 Черновик",
        "ACTIVE": "✅ Активна",
        "ABORTED": "❌ Отменена",
    }
    status_display = status_map.get(vacancy["status"], vacancy["status"])

    await state.update_data(current_vacancy_id=vacancy_id)

    await callback.message.edit_text(
        texts.VACANCY_DETAIL.format(
            id=vacancy_id,
            track=track_name,
            status=status_display,
            description=vacancy["description"],
            viewed=stats.get("viewed", 0) if stats else 0,
            selected=stats.get("selected", 0) if stats else 0,
            rejected=stats.get("rejected", 0) if stats else 0,
            total=stats.get("total_candidates", 0) if stats else 0,
        ),
        reply_markup=vacancy_detail_keyboard(vacancy_id),
    )
    await state.set_state(HMStates.viewing_vacancy)

