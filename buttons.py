
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    resize_keyboard=True
).add("Add reminder")

cancel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add("Cancel")

choice_kb = ReplyKeyboardMarkup(
    resize_keyboard=True
).row(
    KeyboardButton("Yes"),
    KeyboardButton("No")
).row(
    KeyboardButton("Cancel")
)
