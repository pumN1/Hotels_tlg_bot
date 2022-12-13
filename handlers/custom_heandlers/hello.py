from loader import bot
from states.user_info import MyStates
from telebot.types import Message


@bot.message_handler(commands=['hello_world'])
@bot.message_handler(func=lambda message: message.text == "Привет")
def hello_world(message: Message) -> None:
    bot.set_state(message.from_user.id, MyStates.name, message.chat.id)
    bot.send_message(message.chat.id, 'Привет, {user}! Как я могу к вам обращаться?'.format(
        user=message.from_user.username))


@bot.message_handler(state=MyStates.name)
def get_name(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.chat.id, 'Приятно познакомиться!')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
    else:
        bot.send_message(message.chat.id, 'Имя может содержать только буквы')
