import emoji
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

"""
This code defines two keyboards, kb_weather and kb_weather_cancel, 
which are both instances of ReplyKeyboardMarkup from the aiogram.types module. 
The resize_keyboard argument is set to True for both instances, meaning that the 
size of the keyboard will be automatically adjusted to fit the space available in the chat window.
The kb_weather keyboard contains a single button labeled "Weather :sun_behind_cloud:", 
and the kb_weather_cancel keyboard contains a single button labeled "Cancel :cross_mark:". 
The keyboards are created using the ReplyKeyboardMarkup class and the add method, which allows you to add buttons to the keyboard.
This code defines a buttons dictionary that contains two buttons, 'button_weather' and 
'button_cancel', both instances of the KeyboardButton class from the aiogram.types module.
The text for each button is specified as an argument to the KeyboardButton constructor.
"""

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

