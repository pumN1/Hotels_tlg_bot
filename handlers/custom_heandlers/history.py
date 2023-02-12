import json
from loader import bot
from telebot.types import Message, CallbackQuery
from states.user_info import MyStates
from keyboards.inline import user_history
from handlers.custom_heandlers import general
from peewee import *


@bot.message_handler(commands=['history'])
def get_history(message: Message) -> None:
    bot.set_state(message.from_user.id, MyStates.history, message.chat.id)
    user_id = message.from_user.id
    bot.send_message(message.chat.id, 'Последние Ваши запросы:',
                     reply_markup=user_history.history_req(user_id))


@bot.callback_query_handler(func=None, state=MyStates.history)
def call_history(call: CallbackQuery) -> None:
    hotel_list = [[hotel.hotel_link, json.loads(hotel.hotel_info), hotel.hotel_id]
                  for hotel in general.Hotel.select().where(general.Hotel.id_query == call.data)]
    general.send_query_results(chat_id=call.message.chat.id, hotels=hotel_list)
    bot.set_state(call.from_user.id, MyStates.dop_info, call.message.chat.id)
