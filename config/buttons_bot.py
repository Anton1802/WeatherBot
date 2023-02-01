import emoji
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Buttons
buttons = {
    'button_weather': KeyboardButton(emoji.emojize('Weather :sun_behind_cloud:')),
    'button_cancel': KeyboardButton(emoji.emojize("Cancel :cross_mark:"))
}

# Keyboards
keyboards = {
    'kb_weather': ReplyKeyboardMarkup(resize_keyboard=True),
    'kb_weather_cancel': ReplyKeyboardMarkup(resize_keyboard=True)
}
keyboards['kb_weather_cancel'].add(buttons['button_cancel'])
keyboards['kb_weather'].add(buttons['button_weather'])

