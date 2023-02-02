import re
from loader import bot
from states.user_info import MyStates
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from utils.misc import reqeust
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime, date, timedelta
from keyboards.inline import city_clarification, additional_info


@bot.message_handler(state=MyStates.city)
def get_local_city(message: Message) -> None:
    if re.fullmatch(r'[^\d\n]*', message.text):
        bot.set_state(message.from_user.id, MyStates.local_city, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text

        bot.send_message(message.chat.id, 'Уточните, пожалуйста:', reply_markup=city_clarification.city_markup(message.text))
    else:
        bot.send_message(message.chat.id, 'Город может содержать только буквы')


@bot.callback_query_handler(func=None, state=MyStates.local_city)
def call_local_city(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['local_city'] = call.data
        if data['command'] == 'bestdeal':
            bot.set_state(call.from_user.id, MyStates.price_range, call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Укажите желаемый диапазон цен за отель в формате min-max.')
        elif call.data:
            bot.set_state(call.from_user.id, MyStates.num_hotels, call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Сколько отелей показать (максимум 6)?')


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


@bot.message_handler(state=MyStates.date_out)
def get_date_out(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        result = data['date_in'] + timedelta(days=int(message.text))
        data['date_out'] = result
        bot.send_message(message.chat.id, 'Дата выезда: {date_ar}'.format(date_ar=result))
    loading_id = bot.send_message(message.chat.id, 'Ищем..')

    data_hotels = reqeust.get_hotels(data)

    if data_hotels:
        bot.delete_message(message.chat.id, loading_id.message_id)
        for i_mes in data_hotels:
            bot.send_photo(message.chat.id, photo=i_mes[0],
                           caption='\n'.join([f'{key} {value}' for key, value in i_mes[1].items()]),
                           reply_markup=additional_info.dop_markup(i_mes[2]), allow_sending_without_reply=True)


@bot.callback_query_handler(func=None)
def call_dop_info(call: CallbackQuery) -> None:
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
