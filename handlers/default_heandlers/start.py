from telebot.types import Message
from loader import bot
from states.user_info import MyStates


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}! Выбери одну из команд для поиска")

