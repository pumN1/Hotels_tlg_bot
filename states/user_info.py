from telebot.handler_backends import State, StatesGroup


class MyStates(StatesGroup):
    command = State()
    city = State()
    local_city = State()
    num_hotels = State()
    date_in = State()
    date_out = State()
    price_range = State()
    dist_range = State()
