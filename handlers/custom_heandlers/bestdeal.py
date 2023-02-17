from loguru import logger

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


def get_hotels_list(hotels_list: List, price_range: str, dist_range: str, num_hotels: int) -> List:
    dist_min, dist_max = map(int, dist_range.split('-'))
    price_min, price_max = map(int, price_range.split('-'))
    # dist_min = int(dist_range.split('-')[0])
    # dist_max = int(dist_range.split('-')[1])
    upd_hot_list = []
    hotels_dict = dict()
    for hotel in hotels_list:
        current_dist = hotel.get('destinationInfo').get('distanceFromDestination').get('value')
        current_price = hotel['price']['lead']['amount']
        hotels_dict[hotel.get('name')] = [current_dist, current_price]
        if dist_min <= current_dist <= dist_max:
            if price_min <= current_price <=  price_max:
                upd_hot_list.append(hotel)
                if len(upd_hot_list) == num_hotels:
                    break
    logger.info(hotels_dict)
    return upd_hot_list
