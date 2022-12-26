import logging
import time

from tg_bot import bot

while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except OSError:
        logging.critical('Ошибка подключения к tg API.')
        time.sleep(10)
