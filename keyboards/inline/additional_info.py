from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def dop_markup(id_hotel):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text='Фото', callback_data=f'{id_hotel}'),
        InlineKeyboardButton(text='Ссылка на сайт', url=f'https://www.hotels.com/h{id_hotel}.Hotel-Information')
    )
    return keyboard