from aiogram.fsm.state import State, StatesGroup

class LeadForm(StatesGroup):
    full_name = State()
    phone_number = State()
    english_level = State()
    region = State()
    answering_questions = State()

class AdminReply(StatesGroup):
    waiting_for_reply = State()
    target_user_id = State()