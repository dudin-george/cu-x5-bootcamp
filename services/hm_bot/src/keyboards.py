"""Keyboard builders for HM bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Создать вакансию", callback_data="create_vacancy")],
        [InlineKeyboardButton(text="📋 Мои вакансии", callback_data="my_vacancies")],
    ])


def tracks_keyboard(tracks: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard with track selection."""
    buttons = []
    for track in tracks:
        buttons.append([
            InlineKeyboardButton(
                text=track["name"],
                callback_data=f"track_{track['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_vacancy_keyboard() -> InlineKeyboardMarkup:
    """Confirm vacancy creation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish_vacancy")],
        [InlineKeyboardButton(text="✏️ Изменить описание", callback_data="edit_description")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="abort_vacancy")],
    ])


def vacancies_keyboard(vacancies: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard with vacancy list."""
    buttons = []
    for v in vacancies:
        # Truncate description for button text
        desc = v.get("description", "")[:30]
        if len(v.get("description", "")) > 30:
            desc += "..."
        buttons.append([
            InlineKeyboardButton(
                text=f"📌 {desc}",
                callback_data=f"vacancy_{v['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vacancy_detail_keyboard(vacancy_id: int) -> InlineKeyboardMarkup:
    """Vacancy detail actions keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎯 Подобрать кандидата",
            callback_data=f"pick_{vacancy_id}"
        )],
        [InlineKeyboardButton(text="🔙 К списку", callback_data="my_vacancies")],
    ])


def candidate_actions_keyboard(vacancy_id: int, candidate_id: str) -> InlineKeyboardMarkup:
    """Candidate review actions (Tinder mode)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Пригласить",
                callback_data=f"invite_{vacancy_id}_{candidate_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⏭️ Пропустить",
                callback_data=f"skip_{vacancy_id}_{candidate_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"reject_{vacancy_id}_{candidate_id}"
            ),
        ],
        [InlineKeyboardButton(
            text="🔙 К вакансии",
            callback_data=f"vacancy_{vacancy_id}"
        )],
    ])


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel action keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ])

