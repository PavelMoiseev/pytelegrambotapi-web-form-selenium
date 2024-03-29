import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from datetime import datetime
from pathlib import Path

# Использовать если не получилось установить веб-драйвер
# from webdriver_manager.firefox import GeckoDriverManager

# Используем веб-драйвер для браузера Firefox (заменить при необходимости)
# browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())


def fill_fields_form(user_id, user_data):
    option = webdriver.FirefoxOptions()
    option.headless = True              # Отображение браузера

    browser = webdriver.Firefox(options=option)
    form_url = 'https://b24-iu5stq.bitrix24.site/backend_test/'
    # Логика заполнения формы (постраничное заполнение)
    # Первая страница
    try:
        browser.get(form_url)
        name_form_field = 'name'
        last_name_form_field = 'lastname'
        browser.find_element(By.NAME, name_form_field).send_keys(user_data.name)
        browser.find_element(By.NAME, last_name_form_field).send_keys(user_data.last_name)
        button_1_css_selector = 'button.b24-form-btn:nth-child(1)'
        browser.find_element(By.CSS_SELECTOR, button_1_css_selector).click()
        time.sleep(0.5)
    except Exception as error:
        print('Ошибка при заполнении первой страницы формы.', error)
    # Вторая страница
    try:
        email_form_field = 'email'
        phone_form_field = 'phone'
        browser.find_element(By.NAME, email_form_field).send_keys(user_data.email)
        browser.find_element(By.NAME, phone_form_field).send_keys(user_data.phone)
        button_2_css_selector = 'div.b24-form-btn-block:nth-child(2) > button:nth-child(1)'
        browser.find_element(By.CSS_SELECTOR, button_2_css_selector).click()
        time.sleep(0.5)
    except Exception as error:
        print('Ошибка при заполнении второй страницы формы.', error)
    # Третья страница
    try:
        birthday_format = '%d.%m.%Y'
        date_of_birth = datetime.strptime(user_data.birth, birthday_format)
        # Открыть календарь
        calendar_css_selector = '.b24-form-control'
        browser.find_element(By.CSS_SELECTOR, calendar_css_selector).click()
        # Выбрать год рождения
        year_css_selector = 'div.vdpPeriodControl:nth-child(2) > select:nth-child(2)'
        from_year = browser.find_element(By.CSS_SELECTOR, year_css_selector)
        select_year = Select(from_year)
        select_year.select_by_visible_text(str(date_of_birth.year))
        # Выбрать месяц рождения
        month_css_selector = 'div.vdpPeriodControl:nth-child(1) > select:nth-child(2)'
        from_moth = browser.find_element(By.CSS_SELECTOR, month_css_selector)
        select_month = Select(from_moth)
        month_number = date_of_birth.month - 1  # Месяц в календаре формы считается с 0
        select_month.select_by_index(month_number)
        # Выбрать день
        day_number = date_of_birth.day
        send_button_css_selector = 'div.b24-form-btn-container:nth-child(4) > div:nth-child(2) > button:nth-child(1)'
        days_xpath = '//table//td[@class="vdpCell selectable"]//div[@class="vdpCellContent"]'
        days_from_table = browser.find_elements(By.XPATH, days_xpath)
        for item in days_from_table:
            if day_number == int(item.get_attribute('innerHTML')):
                item.click()
                browser.find_element(By.CSS_SELECTOR, send_button_css_selector).click()
                break
    except Exception as error:
        print('Ошибка при заполнении календаря.', error)

    time.sleep(3)
    try:
        # Сохранить скриншот
        dir_path = Path.cwd()
        time_now = datetime.now()
        time_format = time_now.strftime("%Y-%m-%d_%H:%M")
        screenshots_path = Path(dir_path, 'screenshots', f'{time_format}_{user_id}.jpg')
        browser.save_screenshot(screenshots_path)
    except Exception as error:
        print('Ошибка сохранения скриншота.', error)


# Проверить доступность формы
def fill_web_form(user_id, user_data):
    try:
        fill_fields_form(user_id, user_data)
    except Exception as error:
        print("Форма недоступна, ожидание возобновления доступа.", error)
        time.sleep(600)
        fill_web_form(user_id, user_data)
