from loader import bot
from states.user_info import MyStates
from telebot.types import Message


@bot.message_handler(commands=['lowprice'])
def get_city(message: Message) -> None:
    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'lowprice'
    bot.send_message(message.chat.id, 'Какой город интересует?')
