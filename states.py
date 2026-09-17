from aiogram.fsm.state import State, StatesGroup

class LeadForm(StatesGroup):
    region = State()
    q1 = State()
    q2 = State()
    q3 = State()

class AdminReply(StatesGroup):
    waiting_for_reply = State()
    target_user_id = State()