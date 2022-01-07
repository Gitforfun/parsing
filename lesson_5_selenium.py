#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By  # для сбособа выбора элементов на странице
from selenium.webdriver.chrome.options import Options  # в нашем случае, для размера окна
# from selenium.webdriver.common.action_chains import ActionChains  # манипулятивные действия
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
import hashlib


def create_hash(dict, string):
    """ создание хеш, по ключу из словаря. Возвращает хеш или None """
    try:
        hash = (str(dict[string])).encode()
    except:
        print(f'ERROR!! {string}:{dict[string]}.')
        return None
    else:
        index_hash = hashlib.md5(hash).hexdigest()
        return index_hash


chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://mvideo.ru')

# промотка страницы
driver.execute_script(f"window.scrollTo (0, {120*14});")

# Переход в группу "В тренде"
#TODO не получается выбрать один элемент из списка найденных
# wait = WebDriverWait(driver, 20)
# button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "//mvid-shelf-group//button[contains(@class,'tab-button')][2]")))

time.sleep(5)
button = driver.find_elements(By.CLASS_NAME, 'tab-button')[1]

try:
    button.click()
except exceptions.TimeoutException as e:
    print('Кнопки "в тренде" нет!')

# Промотка списка по кнопке
while True:
    wait = WebDriverWait(driver, 7)
    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//mvid-shelf-group/mvid-carousel//button[contains(@class, 'forward')]")))  # element_to_be_clickable
        try:
            button.click()
        except exceptions.ElementClickInterceptedException as e:
            print('Finish by unclick')
            break
    except exceptions.TimeoutException as e:
        print('Finish by find button')
        break

# открытие/создание базы mongo
client = MongoClient('127.0.0.1', 27017)  # подключились к серверу
db = client['mvideo']  # создали базу
db_collection = db.collection  # создали коллекцию
db_collection.create_index('hash', unique=True)

# получение данных из списка товаров и внесение в базу
products = driver.find_elements(By.XPATH, "//span[contains(text(), 'В тренде')]/following::mvid-carousel[1]//a[@_ngcontent-serverapp-c242 and not(contains(@class, 'img'))]")
for item in products:
    product_data = {}
    product_data['name'] = item.text
    product_data['link'] = item.get_attribute('href')
    product_data['hash'] = create_hash(product_data, 'name')

    try:
        db_collection.insert_one(product_data)
    except dke:
        print(f"ERROR! Документ {product_data['name']} уже существует!")
print()  # для отладки
driver.close()
