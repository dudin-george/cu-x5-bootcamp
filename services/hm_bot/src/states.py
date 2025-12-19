"""FSM states for HM bot."""

from aiogram.fsm.state import State, StatesGroup


class HMStates(StatesGroup):
    """States for HM bot flows."""

    # Main menu
    in_menu = State()

    # Create vacancy flow
    selecting_track = State()
    entering_description = State()
    confirming_vacancy = State()

    # View vacancies
    viewing_vacancies = State()
    viewing_vacancy = State()

    # Tinder mode
    picking_candidate = State()

