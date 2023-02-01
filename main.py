import logging
import time
import requests
import emoji

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as md

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
    await message.reply(
        md.text(
            md.text(f"Hi, {user_full_name}."),
            md.text(f"Please enter command: /weather"),
            sep="\n"
        )
    )


@dp.message_handler(commands='weather')
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
        result_json = requests.get(
            f"https://weather.visualcrossing.com/"
            f"VisualCrossingWebServices/rest/services/"
            f"timeline/{city}?unitGroup=metric&"
            f"key=4CWDMKRUDWAT7SDEUYABU6ZRD&contentType=json"
        ).json()
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
    except requests.exceptions.JSONDecodeError:
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

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
