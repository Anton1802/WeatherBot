import logging
import time
import requests
import emoji

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as md
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import filters

logging.basicConfig(level=logging.INFO, filename="bot.log", filemode="w")

BOT_TOKEN = "5885516304:AAH6haMHNEyHB1Ivb--m0SzYS1dH-F3Eku0"
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    city = State()


@dp.message_handler(commands='start')
async def start_handle(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    button_weather = KeyboardButton(emoji.emojize('Weather :sun_behind_cloud:'))
    kb_weather = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_weather.add(button_weather)
    await message.reply(md.text(f"Hi, {user_full_name}."), reply_markup=kb_weather)



@dp.message_handler(filters.Text(equals=[emoji.emojize('Weather :sun_behind_cloud:'), '/weather']))
async def start_weather(message: types.Message):
    await Form.city.set()
    await bot.send_message(
        message.chat.id,
        md.text(emoji.emojize(":cityscape: Please enter your city:"), sep="\n")
    )


@dp.message_handler(state=Form.city)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await state.finish()
    city = data['city']
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key=4CWDMKRUDWAT7SDEUYABU6ZRD&contentType=json"
        result_json = requests.get(url).json()
        if result_json is not None:
            adress = result_json['resolvedAddress']
            timezone = result_json['timezone']
            description = result_json['description']
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
            )
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f'{e}, {time.asctime()}')
        await bot.send_message(
            message.chat.id,
            md.text(md.bold(emoji.emojize(":stop_sign: Error: ")), md.code("The request is not correct!")),
            parse_mode="MarkdownV2"
        )

    await bot.send_message(
        message.chat.id,
        md.text(md.bold("Thank you for contacting!"), sep="\n"),
        parse_mode="MarkdownV2"
    )

    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id}, {user_full_name}, {city}, {time.asctime()}')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
