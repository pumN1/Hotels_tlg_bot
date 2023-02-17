from loader import bot
from states.user_info import MyStates
from telebot.types import Message
from typing import List
import re


@bot.message_handler(commands=['bestdeal'])
def get_city(message: Message) -> None:
    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'bestdeal'
    bot.send_message(message.chat.id, 'Какой город интересует?')


@bot.message_handler(state=MyStates.price_range)
def get_price_min(message: Message) -> None:
    if re.fullmatch(r'\d+-\d+', message.text):
        bot.set_state(message.from_user.id, MyStates.dist_range, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_range'] = message.text
        bot.send_message(message.chat.id, 'Укажите диапазон расстояний отеля от центра в формате min-max.')
    else:
        bot.send_message(message.chat.id, 'Неверный формат. Попробуйте еще раз')


@bot.message_handler(state=MyStates.dist_range)
def get_price_min(message: Message) -> None:
    if re.fullmatch(r'\d+-\d+', message.text):
        bot.set_state(message.from_user.id, MyStates.num_hotels, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_range'] = message.text
        bot.send_message(message.chat.id, 'Сколько отелей показать (максимум 6)?')
    else:
        bot.send_message(message.chat.id, 'Неверный формат. Попробуйте еще раз')


def get_hotels_list(hotels_list: List, dist_range: str, num_hotels: int) -> List:
    dist_min = int(dist_range.split('-')[0])
    dist_max = int(dist_range.split('-')[1])
    upd_hot_list = []
    for hotel in hotels_list:
        if dist_min <= hotel.get('destinationInfo').get('distanceFromDestination').get('value') <= dist_max:
            upd_hot_list.append(hotel)
            if len(upd_hot_list) == num_hotels:
                break
    return upd_hot_list
