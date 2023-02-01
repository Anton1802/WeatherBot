import logging
import time
import emoji
import requests

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram import filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config.data_bot as conf_d
import config.buttons_bot as conf_b

logging.basicConfig(level=logging.INFO, filename="bot.log", filemode="w")

bot = Bot(token=conf_d.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    city = State()


@dp.message_handler(commands='start')
async def start_handle(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    await message.reply(md.text(f"Hi, {user_full_name}."), reply_markup=conf_b.keyboards['kb_weather'])


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


@dp.message_handler(filters.Text(equals=emoji.emojize("Cancel :cross_mark:")), state="*")
@dp.message_handler(state="*", commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info(f"Canceling state %r", current_state)
    await state.finish()
    await message.reply("Cancelled request!", reply_markup=conf_b.keyboards['kb_weather'])


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
