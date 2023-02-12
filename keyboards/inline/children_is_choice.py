from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def choices():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text='Да', callback_data='yes'),
        InlineKeyboardButton(text='нет', callback_data='no')
    )
    return keyboard