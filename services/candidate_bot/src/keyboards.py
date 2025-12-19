"""Keyboard builders."""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)


def make_keyboard(
    items: list[str],
    add_other: bool = False,
    request_contact: bool = False,
    row_width: int = 2,
) -> ReplyKeyboardMarkup:
    """Create a reply keyboard from list of strings.
    
    Args:
        items: Button labels.
        add_other: Add "Другое" button.
        request_contact: Add contact request button.
        row_width: Buttons per row.
        
    Returns:
        ReplyKeyboardMarkup.
    """
    buttons = []
    
    if request_contact:
        buttons.append([
            KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
        ])

    row = []
    for item in items:
        row.append(KeyboardButton(text=item))
        if len(row) == row_width:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    if add_other:
        buttons.append([KeyboardButton(text="Другое")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def make_inline_keyboard(
    items: list[tuple[str, str]],
    row_width: int = 2,
) -> InlineKeyboardMarkup:
    """Create inline keyboard.
    
    Args:
        items: List of (text, callback_data) tuples.
        row_width: Buttons per row.
        
    Returns:
        InlineKeyboardMarkup.
    """
    buttons = []
    row = []
    
    for text, callback_data in items:
        row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        if len(row) == row_width:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Pre-built keyboards
REMOVE_KEYBOARD = ReplyKeyboardRemove()

QUIZ_ANSWER_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="A", callback_data="quiz_ans_A"),
        InlineKeyboardButton(text="B", callback_data="quiz_ans_B"),
    ],
    [
        InlineKeyboardButton(text="C", callback_data="quiz_ans_C"),
        InlineKeyboardButton(text="D", callback_data="quiz_ans_D"),
    ],
])

