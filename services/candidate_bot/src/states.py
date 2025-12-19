"""FSM states for candidate form."""

from aiogram.fsm.state import State, StatesGroup


class InternForm(StatesGroup):
    """States for intern application form."""
    
    # Initial choice
    waiting_for_choice = State()
    upload_resume = State()
    
    # Form fields
    surname = State()
    name = State()
    phone = State()
    email = State()
    resume_link = State()
    priority1 = State()
    priority2 = State()
    course = State()
    course_custom = State()
    university = State()
    university_custom = State()
    specialty = State()
    employment_hours = State()
    city = State()
    city_custom = State()
    source = State()
    source_custom = State()
    birth_year = State()
    citizenship = State()
    citizenship_custom = State()
    tech_stack = State()
    
    # Confirmation
    confirm = State()
    
    # Quiz
    selecting_track = State()  # Выбор трека из API
    in_quiz = State()          # Прохождение квиза

