from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from peewee import *
from handlers.custom_heandlers import general


def history_req(user):
    keyboard = InlineKeyboardMarkup()
    data_base = general.PersonRequest.select().where(general.PersonRequest.id_chat == user).order_by(
        general.PersonRequest.id.asc()).limit(5)
    for req in data_base:
        btn = InlineKeyboardButton(text=f'Запрос {req.date_time} {req.commands}, найдено отелей: {req.results}',
                                   callback_data=req.id)

        keyboard.add(btn)
    return keyboard
