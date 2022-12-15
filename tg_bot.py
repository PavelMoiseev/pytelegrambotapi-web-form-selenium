import telebot
import os
import phonenumbers

from form_actions import fill_web_form
from email.utils import parseaddr
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_API_TOKEN'))

user_data = {}  # Словарь для хранения данных пользователя


def check_user_exists(message):
    user_id = message.from_user.id
    if user_id in user_data:
        return True
    else:
        user_data[user_id] = ['name', 'last_name', 'email', 'phone', 'birth']
        return user_data


@bot.message_handler(commands=['start'])
def start(start_message, res=False):
    try:
        bot.send_message(start_message.chat.id, 'Привет! Я бот для заполнения формы тестового задания!')
        display_list_commands(start_message)
    except Exception as error:
        print('Ошибка при вводе команды /start.', error)


@bot.message_handler(func=lambda message: message.text != '/add_data')
def display_list_commands(input_message):
    try:
        bot.send_message(input_message.chat.id, 'Команды:\n'
                                                '/add_data - ввод данных для заполнения формы.')
    except Exception as error:
        print('Ошибка вывода списка команд.', error)


@bot.message_handler(commands=['add_data'])
def handle_add_data_command(message):
    try:
        mes = bot.send_message(message.chat.id, 'Введите Ваше имя:')
        bot.register_next_step_handler(mes, handle_first_name)
    except Exception as error:
        print('Ошибка обработки команды /add_data.', error)


def handle_first_name(message):
    if write_first_name(message):
        try:
            mes = bot.send_message(message.chat.id, 'Введите Вашу фамилию:')
            bot.register_next_step_handler(mes, handle_last_name)
        except Exception as error:
            print('Ошибка обработки имени.', error)
    else:
        try:
            error_message = bot.send_message(message.chat.id, 'Неверный формат имени, введите имя:')
            bot.register_next_step_handler(error_message, handle_first_name)
        except Exception as error:
            print('Ошибка перенаправления при валидации имени.', error)


def write_first_name(message):
    if validate_name(message.text):
        check_user_exists(message)
        user_data[message.from_user.id][0] = message.text
        return True


def handle_last_name(message):
    if write_last_name(message):
        try:
            mes = bot.send_message(message.chat.id, 'Введите Ваш email:')
            bot.register_next_step_handler(mes, handle_email_address)
        except Exception as error:
            print('Ошибка обработки фамилии.', error)
    else:
        try:
            error_message = bot.send_message(message.chat.id, 'Неверный формат фамилии, введите фамилию:')
            bot.register_next_step_handler(error_message, handle_last_name)
        except Exception as error:
            print('Ошибка перенаправления при валидации фамилии.', error)


def write_last_name(message):
    if validate_name(message.text):
        user_data[message.from_user.id][1] = message.text
        return True


def handle_email_address(message):
    if write_email_address(message):
        try:
            mes = bot.send_message(message.chat.id, 'Введите Ваш номер телефона, начиная с +7...:')
            bot.register_next_step_handler(mes, handle_phone_number)
        except Exception as error:
            print('Ошибка обработки email адреса.', error)
    else:
        try:
            error_message = bot.send_message(message.chat.id, 'Неверный формат email адреса, введите email:')
            bot.register_next_step_handler(error_message, handle_email_address)
        except Exception as error:
            print('Ошибка перенаправления при валидации email адреса.', error)


def write_email_address(message):
    if validate_email(message.text):
        user_data[message.from_user.id][2] = message.text
        return True


def handle_phone_number(message):
    if write_phone_number(message):
        try:
            mes = bot.send_message(message.chat.id, 'Введите Вашу дату рождения (формат: dd.mm.yyyy):')
            bot.register_next_step_handler(mes, handle_date_of_birth)
        except Exception as error:
            print('Ошибка обработки номера телефона.', error)
    else:
        try:
            error_message = bot.send_message(message.chat.id, 'Неверный формат номера телефона, введите номер телефона:')
            bot.register_next_step_handler(error_message, handle_phone_number)
        except Exception as error:
            print('Ошибка перенаправления при валидации номера телефона.', error)


def write_phone_number(message):
    if validate_phone_number(message.text):
        user_data[message.from_user.id][3] = message.text
        return True


def handle_date_of_birth(message):
    if write_date_of_birth(message):
        try:
            check_data(message)
        except Exception as error:
            print('Ошибка обработки даты рождения.', error)
    else:
        try:
            error_message = bot.send_message(message.chat.id, 'Неверный формат даты рождения, введите дату рождения:')
            bot.register_next_step_handler(error_message, handle_date_of_birth)
        except Exception as error:
            print('Ошибка перенаправления при валидации даты рождения.', error)


def write_date_of_birth(message):
    if validata_date_of_birth(message.text):
        user_data[message.from_user.id][4] = message.text
        return True


# Вывод клавиатуры проверки или отправления данных
def check_data(message):
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('Редактировать', callback_data='check.edit'),
            telebot.types.InlineKeyboardButton('Отправить', callback_data='check.send'))
        bot.send_message(message.chat.id, ' | '.join(user_data[message.from_user.id]), reply_markup=keyboard)
    except Exception as error:
        print('Ошибка проверки введенных данных.', error)


# Операции первой клавиатуры
@bot.callback_query_handler(func=lambda call: call.data.startswith('check.'))
def callback_query(call):
    try:
        req = call.data
        if req == 'check.edit':
            edit_user_data(call)
        if req == 'check.send':
            fill_web_form(call.message.chat.id, user_data[call.message.chat.id])
            stop_message_handler(call.message)
    except Exception as error:
        print('Ошибка взаимодействия с клавиатурой проверки данных.', error)


# Вывод клавиатуры редактирования
def edit_user_data(call):
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('Имя', callback_data='edit.edit_name'),
            telebot.types.InlineKeyboardButton('Фамилия', callback_data='edit.edit_last_name'),
            telebot.types.InlineKeyboardButton('email', callback_data='edit.edit_email'))
        keyboard.row(
            telebot.types.InlineKeyboardButton('Номер телефона', callback_data='edit.edit_phone_number'),
            telebot.types.InlineKeyboardButton('Дата рождения', callback_data='edit.edit_date_of_birth'))
        bot.send_message(call.message.chat.id, 'Выберите поле для редактирования:', reply_markup=keyboard)
    except Exception as error:
        print('Ошибка выбора поля для редактирования.', error)


# Операции второй клавиатуры
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit.'))
def edit_selected_data(call):
    try:
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
    except Exception as error:
        print('Ошибка взаимодйствия с клавиатурой редактирования данных.', error)


def write_edit_first_name(message):
    try:
        if write_first_name(message):
            check_data(message)
        else:
            error_message = bot.send_message(message.chat.id, 'Неверный формат имени, введите имя:')
            bot.register_next_step_handler(error_message, write_edit_first_name)
    except Exception as error:
        print('Ошибка редактирования имени.', error)


def write_edit_last_name(message):
    try:
        if write_last_name(message):
            check_data(message)
        else:
            error_message = bot.send_message(message.chat.id, 'Неверный формат фамилии, введите фамилию:')
            bot.register_next_step_handler(error_message, write_edit_last_name)
    except Exception as error:
        print('Ошибка редактирования фамилии.', error)


def write_edit_email_address(message):
    try:
        if write_email_address(message):
            check_data(message)
        else:
            error_message = bot.send_message(message.chat.id, 'Неверный формат email адреса, введите email:')
            bot.register_next_step_handler(error_message, write_edit_email_address)
    except Exception as error:
        print('Ошибка редактирования email адреса.', error)


def write_edit_phone_number(message):
    try:
        if write_phone_number(message):
            check_data(message)
        else:
            error_message = bot.send_message(message.chat.id, 'Неверный формат номера телефона, введите номер телефона:')
            bot.register_next_step_handler(error_message, write_edit_phone_number)
    except Exception as error:
        print('Ошибка редактирования номера телефона.', error)


def write_edit_date_of_birth(message):
    try:
        if write_date_of_birth(message):
            check_data(message)
        else:
            error_message = bot.send_message(message.chat.id, 'Неверный формат даты рождения, введите дату рождения:')
            bot.register_next_step_handler(error_message, write_edit_date_of_birth)
    except Exception as error:
        print('Ошибка редактирования даты рождения.', error)


# Поиск и отправка скриншота для конкретного пользователя
def stop_message_handler(message):
    try:
        path_screen = './screenshots/'
        for rootdir, dirs, screens in os.walk(path_screen):
            for screen in screens:
                user_screen = (screen.split('_')[-1].removesuffix('.jpg'))
                if str(message.chat.id) == user_screen:
                    bot.send_photo(message.chat.id, open(f'./screenshots/{screen}', 'rb'))
                    break
        bot.send_message(message.chat.id, 'Спасибо за потраченное время!')
    except Exception as error:
        print('Ошибка поиска и отображения скриншота.', error)


def validate_name(name):
    if name.isalpha():
        return True


def validate_email(email):
    try:
        email = parseaddr(email)[1]
        email_domain = email.split('.')[-1]
        if email and '@' in email and '.' in email and len(email_domain) > 1:
            return True
    except ValueError:
        return False


def validate_phone_number(phone):
    try:
        phone_number = phonenumbers.parse(phone)
        if phonenumbers.is_possible_number(phone_number):
            return True
    except Exception as error:
        print("Несуществующий номер телефона", error)
        return False


def validata_date_of_birth(birthday):
    birthday_format = '%d.%m.%Y'
    year = birthday.split('.')[-1]
    try:
        res = bool(datetime.strptime(birthday, birthday_format))
        if int(year) in range(1902, 2002):
            return res
    except ValueError:
        return False


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
