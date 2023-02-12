from utils.misc import reqeust
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(user_city):
    data_resp = reqeust.city_detail_request(user_city)
    cities = [{'destination_id': region['regionId'], 'city_name': region['name']} for region in data_resp]
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.row(InlineKeyboardButton(text=city['city_name'],
                                              callback_data=city['destination_id']))
    return destinations
