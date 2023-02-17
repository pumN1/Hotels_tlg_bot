from loguru import logger
import json
import re
from loader import bot
from states.user_info import MyStates
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from utils.misc import reqeust
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime, date, timedelta
from keyboards.inline import city_clarification, additional_info, children_is_choice
from peewee import *


db = SqliteDatabase('database/history.db')


class PersonRequest(Model):
    id_chat = IntegerField()
    date_time = DateTimeField()
    commands = CharField()
    results = IntegerField()

    class Meta:
        database = db  # модель будет использовать базу данных 'history.db'


class Hotel(Model):
    id_query = IntegerField()
    hotel_link = CharField()
    hotel_info = TextField()
    hotel_id = IntegerField()

    class Meta:
        database = db


PersonRequest.create_table()
Hotel.create_table()


@bot.message_handler(state=MyStates.city)
def get_local_city(message: Message) -> None:
    if re.fullmatch(r'[^\d\n]*', message.text):
        bot.set_state(message.from_user.id, MyStates.local_city, message.chat.id)
        data_resp = reqeust.city_request(message.text
                                         )
        if not data_resp:
            bot.send_message(message.chat.id, 'Такой город не найден, попробуйте еще раз.')
            bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Уточните, пожалуйста:',
                             reply_markup=city_clarification.city_markup(data_resp))
    else:
        bot.send_message(message.chat.id, 'Город может содержать только буквы')


@bot.callback_query_handler(func=None, state=MyStates.local_city)
def call_local_city(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['local_city'] = call.data
    bot.set_state(call.from_user.id, MyStates.num_adults, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Введите количество взрослых:')


@bot.message_handler(state=MyStates.num_adults)
def get_adults_pass(message: Message) -> None:
    if message.text.isdigit():
        bot.set_state(message.from_user.id, MyStates.num_children, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['num_adults'] = int(message.text)
    bot.send_message(message.chat.id, 'Будут ли с вами дети?', reply_markup=children_is_choice.choices())


@bot.callback_query_handler(func=None, state=MyStates.num_children)
def call_children_pass(call: CallbackQuery) -> None:
    if call.data == 'no':
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['num_children'] = []
            if data['command'] == 'bestdeal':
                bot.set_state(call.from_user.id, MyStates.price_range, call.message.chat.id)
                bot.send_message(call.message.chat.id, 'Укажите желаемый диапазон цен за отель в формате min-max.')
            elif call.data:
                bot.set_state(call.from_user.id, MyStates.num_hotels, call.message.chat.id)
                bot.send_message(call.message.chat.id, 'Сколько отелей показать (максимум 6)?')
    elif call.data == 'yes':
        bot.set_state(call.from_user.id, MyStates.age_children, call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Введите возраст детей через пробел:')


@bot.message_handler(state=MyStates.age_children)
def get_children_is_age(message: Message) -> None:
    if all(num.isdigit() or num.isspace() for num in message.text):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            children_list = []
            for age in message.text.split():
                children_list.append(dict(age=int(age)))
            data['num_children'] = children_list
            if data['command'] == 'bestdeal':
                bot.set_state(message.from_user.id, MyStates.price_range, message.chat.id)
                bot.send_message(message.chat.id, 'Укажите желаемый диапазон цен за отель в формате min-max.')
            else:
                bot.set_state(message.from_user.id, MyStates.num_hotels, message.chat.id)
                bot.send_message(message.chat.id, 'Сколько отелей показать (максимум 6)?')
    else:
        bot.send_message(message.chat.id, 'Возраст может быть только цифрами')


@bot.message_handler(state=MyStates.num_hotels)
def get_date_in(message: Message) -> None:
    if message.text.isdigit() and int(message.text) <= 6:
        bot.set_state(message.from_user.id, MyStates.date_in, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['num_hotels'] = message.text

        LSTEP: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
        bot.send_message(message.chat.id,
                         f"Выберите дату заезда: {LSTEP[step]}",
                         reply_markup=calendar)
    else:
        bot.send_message(message.chat.id, 'Извините, максимально можно вывести только 6 отелей :(')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def get_calendar(call):
    LSTEP: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    bot.set_state(call.from_user.id, MyStates.date_out, call.message.chat.id)
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today(),
                                                 max_date=date.today()+timedelta(days=500)).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали: {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['date_in'] = result
        bot.send_message(call.message.chat.id, 'Сколько ночей?')


def send_query_results(chat_id: int, hotels: list) -> None:
    for i_hotel in hotels:
        bot.send_photo(chat_id, photo=i_hotel[0],
                       caption='\n'.join([f'{key} {value}' for key, value in i_hotel[1].items()]),
                       reply_markup=additional_info.dop_markup(i_hotel[2]), allow_sending_without_reply=True)


@bot.message_handler(state=MyStates.date_out)
def get_date_out(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        result = data['date_in'] + timedelta(days=int(message.text))
        data['date_out'] = result
        bot.send_message(message.chat.id, 'Дата выезда: {date_ar}'.format(date_ar=result))
    loading_id = bot.send_message(message.chat.id, 'Ищем..')
    logger.debug(data)
    data_hotels = reqeust.get_hotels(data)
    logger.debug(data_hotels)
    if not data_hotels:
        bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено:( '
                                          'Измените критерии и попробуйте еще раз.')
    else:
        new_row = PersonRequest.create(
            id_chat=message.from_user.id,
            date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            commands=data['command'],
            results=len(data_hotels),
        )

        for i_hotel in data_hotels:
            Hotel.create(
                id_query=PersonRequest.get(new_row.id),
                hotel_link=i_hotel[0],
                hotel_info=json.dumps(i_hotel[1]),
                hotel_id=i_hotel[2]
            )
        if data_hotels:
            bot.delete_message(message.chat.id, loading_id.message_id)
            if len(data_hotels) < data['num_hotels']:
                bot.send_message(message.chat.id, 'По вашему запросу найдено всего {} отель(ей)'.format(
                    len(data_hotels)))
            send_query_results(message.chat.id, data_hotels)
        bot.set_state(message.from_user.id, MyStates.dop_info, message.chat.id)


@bot.callback_query_handler(func=None, state=MyStates.dop_info)
def call_dop_info(call: CallbackQuery) -> None:
    if call:
        payload_hotel = {
            "currency": "USD",
            "eapid": 1,
            "locale": "ru_Ru",
            "siteId": 300000001,
            "propertyId": call.data
        }
        hotel_info = reqeust.get_hotels_info(payload_hotel)['propertyGallery']['images']
        photo_list = [InputMediaPhoto(caption=img['image']['description'], media=img['image']['url'])
                      for img in hotel_info if hotel_info.index(img) < 10]
        bot.send_media_group(chat_id=call.message.chat.id, media=photo_list)
