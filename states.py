from aiogram.fsm.state import State, StatesGroup

class ApplicationForm(StatesGroup):
    full_name = State()
    phone_number = State()
    english_level = State()
    region = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()

class AdminReply(StatesGroup):
    waiting_for_reply = State()
    target_user_id = State()
