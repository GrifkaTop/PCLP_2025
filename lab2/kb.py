from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Мой профиль"), KeyboardButton(text="Мои оценки")],
    [KeyboardButton(text="Список курсов")]
], resize_keyboard=True)
