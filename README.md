# PyTelegramBotAPI_web_form_selenium 

#### Телеграм бот, предназначенный для сбора данных пользователей.
#### Полученные данные автоматически заполняются в веб форму. Пользователь получает скриншот подтвержающий заполнение формы.
___
## Bot work examples

#### Сбор данных и проверка корректности ввода:

![img_1.png](images%2Fimg_1.png)

#### Редактирование данных:

![img_2.png](images%2Fimg_2.png)

#### Отправка данных в форму и получение подтверждающего изображения:

![img_3.png](images%2Fimg_3.png)

___

## Installation

#### Заполните файл .env:

```bash
.env
```

#### Выполните следующую команду:

```bash
docker build -t my_tg_bot .
```

#### Запустите соответствующий Docker-контейнер:

```bash
docker run my_tg_bot
```

___

## Alternative installation

#### Выполните следующую команду:

```bash
pip install -r requirements.txt
```

#### Запустите скрипт в следующем файле:

```bash
app/__main__.py
```
