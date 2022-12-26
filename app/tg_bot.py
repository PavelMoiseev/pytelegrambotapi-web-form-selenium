import telebot
import os
import logging

from dotenv import load_dotenv
from typing import Any
from pathlib import Path
from user_db import user_db
from validators import validate_name, validate_email, validate_phone_number, validate_date_of_birth
from form_actions import fill_web_form

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_API_TOKEN'))

logging.basicConfig(level=logging.ERROR, filename="tg_bot_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


@bot.message_handler(commands=['start'])
def start(start_message: Any) -> None:
    bot.send_message(start_message.chat.id, 'Привет! Я бот для заполнения формы тестового задания!')
    display_list_commands(start_message)


@bot.message_handler(commands=['add_data'])
def handle_add_data_command(message: Any) -> None:
    mes = bot.send_message(message.chat.id, 'Введите Ваше имя:')
    bot.register_next_step_handler(mes, handle_first_name)


@bot.message_handler(func=lambda message: True)
def display_list_commands(input_message: Any) -> None:
    bot.send_message(input_message.chat.id, 'Команды:\n'
                                            '/add_data - ввод данных для заполнения формы.')


def handle_first_name(message: Any) -> None:
    user_id = message.chat.id
    first_name = message.text
    if validate_name(first_name):
        user_data = user_db[user_id]
        user_data.name = first_name
        mes = bot.send_message(user_id, 'Введите Вашу фамилию:')
        bot.register_next_step_handler(mes, handle_last_name)
    else:
        error_message = bot.send_message(user_id, 'Неверный формат имени, введите имя:')
        bot.register_next_step_handler(error_message, handle_first_name)


def handle_last_name(message: Any) -> None:
    user_id = message.chat.id
    last_name = message.text
    if validate_name(last_name):
        user_data = user_db[user_id]
        user_data.last_name = last_name
        mes = bot.send_message(message.chat.id, 'Введите Ваш email:')
        bot.register_next_step_handler(mes, handle_email_address)
    else:
        error_message = bot.send_message(message.chat.id, 'Неверный формат фамилии, введите фамилию:')
        bot.register_next_step_handler(error_message, handle_last_name)


def handle_email_address(message: Any) -> None:
    user_id = message.chat.id
    email = message.text
    if validate_email(email):
        user_data = user_db[user_id]
        user_data.email = email
        mes = bot.send_message(user_id, 'Введите Ваш номер телефона, начиная с +7...:')
        bot.register_next_step_handler(mes, handle_phone_number)
    else:
        error_message = bot.send_message(message.chat.id, 'Неверный формат email адреса, введите email:')
        bot.register_next_step_handler(error_message, handle_email_address)


def handle_phone_number(message: Any) -> None:
    user_id = message.chat.id
    phone_number = message.text
    if validate_phone_number(phone_number):
        user_data = user_db[user_id]
        user_data.phone = phone_number
        mes = bot.send_message(user_id, 'Введите Вашу дату рождения (формат: dd.mm.yyyy):')
        bot.register_next_step_handler(mes, handle_date_of_birth)
    else:
        error_message = bot.send_message(message.chat.id,
                                         'Неверный формат номера телефона, введите номер телефона:')
        bot.register_next_step_handler(error_message, handle_phone_number)


def handle_date_of_birth(message: Any) -> None:
    user_id = message.chat.id
    date_of_birth = message.text
    if validate_date_of_birth(date_of_birth):
        user_data = user_db[user_id]
        user_data.birth = date_of_birth
        check_data(message)
    else:
        error_message = bot.send_message(user_id, 'Неверный формат даты рождения, введите дату рождения:')
        bot.register_next_step_handler(error_message, handle_date_of_birth)


# Вывод клавиатуры проверки или отправления данных
def check_data(message: Any) -> None:
    user_id = message.chat.id
    user_data = user_db[user_id]
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Редактировать', callback_data='check.edit'),
        telebot.types.InlineKeyboardButton('Отправить', callback_data='check.send'))
    bot.send_message(message.chat.id, f'{user_data.name} | {user_data.last_name} | {user_data.email} |'
                                      f'{user_data.phone} | {user_data.birth}', reply_markup=keyboard)


# Операции первой клавиатуры
@bot.callback_query_handler(func=lambda call: call.data.startswith('check.'))
def callback_query(call: Any) -> None:
    req = call.data
    if req == 'check.edit':
        edit_user_data(call)
    if req == 'check.send':
        fill_web_form(call.message.chat.id, user_db[call.message.chat.id])
        stop_message_handler(call.message)


# Вывод клавиатуры редактирования
def edit_user_data(call: Any) -> None:
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Имя', callback_data='edit.edit_name'),
        telebot.types.InlineKeyboardButton('Фамилия', callback_data='edit.edit_last_name'),
        telebot.types.InlineKeyboardButton('email', callback_data='edit.edit_email'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Номер телефона', callback_data='edit.edit_phone_number'),
        telebot.types.InlineKeyboardButton('Дата рождения', callback_data='edit.edit_date_of_birth'))
    bot.send_message(call.message.chat.id, 'Выберите поле для редактирования:', reply_markup=keyboard)


# Операции второй клавиатуры
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit.'))
def edit_selected_data(call: Any) -> None:
    req = call.data
    if req == 'edit.edit_name':
        message = bot.send_message(call.message.chat.id, 'Введите Ваше имя:')
        bot.register_next_step_handler(message, write_edit_first_name)
    if req == 'edit.edit_last_name':
        message = bot.send_message(call.message.chat.id, 'Введите Вашу фамилию:')
        bot.register_next_step_handler(message, write_edit_last_name)
    if req == 'edit.edit_email':
        message = bot.send_message(call.message.chat.id, 'Введите Ваш email:')
        bot.register_next_step_handler(message, write_edit_email_address)
    if req == 'edit.edit_phone_number':
        message = bot.send_message(call.message.chat.id, 'Введите Ваш номер телефона:')
        bot.register_next_step_handler(message, write_edit_phone_number)
    if req == 'edit.edit_date_of_birth':
        message = bot.send_message(call.message.chat.id, 'Введите Вашу дату рождения (формат: dd.mm.yyyy):')
        bot.register_next_step_handler(message, write_edit_date_of_birth)


def write_edit_first_name(message: Any) -> None:
    user_id = message.chat.id
    first_name = message.text
    if validate_name(first_name):
        user_data = user_db[user_id]
        user_data.name = first_name
        check_data(message)
    else:
        error_message = bot.send_message(user_id, 'Неверный формат имени, введите имя:')
        bot.register_next_step_handler(error_message, write_edit_first_name)


def write_edit_last_name(message: Any) -> None:
    user_id = message.chat.id
    last_name = message.text
    if validate_name(last_name):
        user_data = user_db[user_id]
        user_data.last_name = last_name
        check_data(message)
    else:
        error_message = bot.send_message(user_id, 'Неверный формат фамилии, введите фамилию:')
        bot.register_next_step_handler(error_message, write_edit_last_name)


def write_edit_email_address(message: Any) -> None:
    user_id = message.chat.id
    email = message.text
    if validate_email(email):
        user_data = user_db[user_id]
        user_data.email = email
        check_data(message)
    else:
        error_message = bot.send_message(user_id, 'Неверный формат email адреса, введите email:')
        bot.register_next_step_handler(error_message, write_edit_email_address)


def write_edit_phone_number(message: Any) -> None:
    user_id = message.chat.id
    phone_number = message.text
    if validate_phone_number(phone_number):
        user_data = user_db[user_id]
        user_data.phone = phone_number
        check_data(message)
    else:
        error_message = bot.send_message(user_id,
                                         'Неверный формат номера телефона, введите номер телефона:')
        bot.register_next_step_handler(error_message, write_edit_phone_number)


def write_edit_date_of_birth(message: Any) -> None:
    user_id = message.chat.id
    date_of_birth = message.text
    if validate_date_of_birth(date_of_birth):
        user_data = user_db[user_id]
        user_data.birth = date_of_birth
        check_data(message)
    else:
        error_message = bot.send_message(user_id, 'Неверный формат даты рождения, введите дату рождения:')
        bot.register_next_step_handler(error_message, write_edit_date_of_birth)


# Поиск и отправка скриншота для конкретного пользователя
def stop_message_handler(message: Any) -> None:
    try:
        dir_path = Path.cwd()
        path_screen = Path(dir_path, 'screenshots')
        for screen in Path(path_screen).glob('*.jpg'):
            path_screen = screen
            screen_str = str(screen).removesuffix('.jpg')
            user_screen = screen_str.split('_')[-1]
            if str(message.chat.id) == user_screen:
                with open(f'{path_screen}', 'rb') as screen_file:
                    bot.send_photo(message.chat.id, screen_file)
                break
        bot.send_message(message.chat.id, 'Спасибо за потраченное время!')
    except FileNotFoundError:
        logging.critical('Ошибка поиска и отображения скриншота.', exc_info=True)
