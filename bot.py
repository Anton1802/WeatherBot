import logging
import time
import emoji
import requests
from translate.translate import Translator

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram import filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config.data_bot as conf_d
import config.buttons_bot as conf_b

# Setting logging
logging.basicConfig(level=logging.INFO, filename="bot.log", filemode="w")

# Bot, storage, dispatcher
bot = Bot(token=conf_d.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    city = State()


'''
This is a function in the python programming language that uses the Telebot API to handle the /start command in a Telegram chatbot. 
The function takes a message parameter of type types.Message which contains information about the user who sent the message. 
The user's ID and full name are extracted from the message object and logged to the console. 
Then, a reply is sent back to the user with the text "Hi, [user full name]." and a keyboard markup specified in conf_b.keyboards['kb_weather'].
'''
@dp.message_handler(commands='start')
async def start_handle(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    await message.reply(md.text(f"Hi, {user_full_name}."), reply_markup=conf_b.keyboards['kb_weather'])

    logging.info(f'{user_id} {user_full_name} {time.asctime()}')


"""
This is a function in the python programming language that uses the Telebot API to handle the /weather 
command or a text message that contains the emoji "Weather :sun_behind_cloud:" in a Telegram chatbot. 
The function sets the "city" field in the Form object to an active state and then sends a message to the user asking them to enter their city. 
The message is sent with a bold text "Please enter your city:" and a keyboard markup specified in conf_b.keyboards['kb_weather_cancel'].
"""
@dp.message_handler(commands='weather')
@dp.message_handler(filters.Text(equals=emoji.emojize('Weather :sun_behind_cloud:')))
async def start_weather(message: types.Message):
    await Form.city.set()

    await bot.send_message(
        message.chat.id,
        md.bold(emoji.emojize(":cityscape: Please enter your city:"), sep="\n"),
        parse_mode="MarkdownV2",
        reply_markup=conf_b.keyboards['kb_weather_cancel']
    )


"""
This is a function in the python programming language that uses the Telebot API to handle either a text message that contains the emoji
"Cancel :cross_mark:" or the /cancel command in a Telegram chatbot. 
The function takes two parameters, a message of type types.Message which contains information about the user's message and a state of type 
FSMContext which is used to store the state of the chatbot's conversation with the user.
The function first checks if the current_state is None and if it is, the function returns without doing anything. 
If the current_state is not None, the function logs that it is canceling the current state and then finishes the state and sends a message 
to the user with the text "Cancelled request!" and a keyboard markup specified in conf_b.keyboards['kb_weather'].
"""
@dp.message_handler(filters.Text(equals=emoji.emojize("Cancel :cross_mark:")), state="*")
@dp.message_handler(state="*", commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info(f"Canceling state %r", current_state)
    await state.finish()
    await message.reply("Cancelled request!", reply_markup=conf_b.keyboards['kb_weather'])

"""
This code is a handler for a Telegram Bot using the python-telegram-bot library. 
When the user inputs the command '/weather' or sends the message 'Weather :sun_behind_cloud:', the bot prompts the user to enter the city. 
After the user inputs the city, the code sends a GET request to an API with the city as a parameter, and retrieves the weather 
information for that city. The response from the API is then parsed to extract information like the city name, time zone, description, maximum
and minimum temperature. The extracted information is then formatted and sent as a message to the user by the bot. 
The message includes the city, time zone, description, maximum, and minimum temperature. 
Finally, the code logs the user's id, name, and the city requested along with the time.
"""
@dp.message_handler(state=Form.city)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await state.finish()

    city = data['city']

    try:
        url_one_part, url_to_part = conf_d.URL_API.split(sep="?")
        url_one_part += city + '?'
        request_api = url_one_part + url_to_part

        result_json = requests.get(request_api).json()

        if result_json is not None:
            translator = Translator(to_lang="ru")
            adress = result_json['resolvedAddress']
            timezone = translator.translate(result_json['timezone'])
            description = translator.translate(result_json['description'])
            max_temp = result_json['days'][0]['tempmax']
            min_temp = result_json['days'][0]['tempmin']

            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text(emoji.emojize(":cityscape: Your city: "), md.bold(adress)),
                    md.text(emoji.emojize(":hourglass_done: Time zone: "), md.code(timezone)),
                    md.text(emoji.emojize(":page_with_curl: Description: "), md.code(description)),
                    md.text(emoji.emojize(":thermometer: Max temperature: "), md.bold(max_temp)),
                    md.text(emoji.emojize(":thermometer: Min temperature: "), md.bold(min_temp)),
                    sep="\n"
                ),
                parse_mode="MarkdownV2",
                reply_markup=conf_b.keyboards['kb_weather']
            )
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f'{e}, {time.asctime()}')

        await bot.send_message(
            message.chat.id,
            md.text(md.bold(emoji.emojize(":stop_sign: Error: ")), md.code("The request is not correct!")),
            parse_mode="MarkdownV2",
            reply_markup=conf_b.keyboards['kb_weather']
        )

    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    logging.info(f'{user_id}, {user_full_name}, {city}, {time.asctime()}')

    await bot.send_message(
        message.chat.id,
        md.text(md.bold(f"Thank {user_full_name} for contacting!"), sep="\n"),
        parse_mode="MarkdownV2"
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
