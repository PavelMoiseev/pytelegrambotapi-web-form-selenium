# Установить базовый образ
FROM python:3.10.4-alpine
# Установить рабочий каталог в контейнере
WORKDIR /my_tg_bot
# Скопировать файл зависимостей в рабочий каталог
COPY requirements.txt .
# Установить зависимости
RUN pip install -r requirements.txt
# Скопировать содержимое локального каталога в рабочий каталог
COPY . .
# Установить токен для телеграмм бота
ENV TOKEN="${TELEGRAM_API_TOKEN}"
# Команда для запуска при запуске контейнера
CMD ["python", "app/__main__.py" ]