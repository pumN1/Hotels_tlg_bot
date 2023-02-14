from utils.misc import reqeust
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(data_resp):
    destinations = InlineKeyboardMarkup()
    for city in data_resp:
        destinations.row(InlineKeyboardButton(text=city['name'],
                                              callback_data=city['destination_id']))
    return destinations
