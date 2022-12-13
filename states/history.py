from  telebot.handler_backends import State, StatesGroup

class Usrs_request(StatesGroup):
    user_command = State()
    date_commands = State()
    hotels = State()