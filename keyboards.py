from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Share Phone Number", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_english_level_keyboard() -> InlineKeyboardMarkup:
    levels = ["A1-A2", "B1", "B2", "C1", "C2"]
    buttons = [[InlineKeyboardButton(text=level, callback_data=f"eng_{level}")] for level in levels]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
