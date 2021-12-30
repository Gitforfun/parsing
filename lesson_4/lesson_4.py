#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep  # добавил для избежания бана. Возможно не актуально, всвязи с медленной работы супа
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
import hashlib

from lxml import html
import requests
from pprint import pprint
from urllib.parse import urlparse


def crawler_lenta(dblenta):
    """
    Краулер новостей с Ленты.ру. Ищет главные новости. Берет ссылку и ее текст. Циклично ереходит по ссылкам и берет
    из первой публикации: дату, автора и, если ранее не удалось вытащить текст, то берет текст.
    Результат записывает в Лист и базу Монго. Но до этого согдает в базе Коллекцию.
    """
    url = 'https://lenta.ru'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
    response = requests.get(url, headers=headers)
    if response.ok:
        dom = html.fromstring(response.text)

        data_lenta = []

        news_links = dom.xpath("//a[contains(@class, 'topnews')]")  # блок со всеми новостями
        for item in news_links:  # для каждого блока
            data_item = {}
            # вытащить краткое содержание, и ссылку
            text = item.xpath('.//span[contains(@class, "card-mini")]/text()')
            try:
                link = item.xpath('@href')[0]
            except:
                link = ''
            else:
                # проверить ссылку на относительность пути
                if not urlparse(link).netloc and not urlparse(link).scheme:
                    link = url + link
                # перейти по ссылке и получить дату/время и автора. Если текст пустой, присвоить тексту заголовок
                responce2 = requests.get(link, headers=headers)
                articl_dom = html.fromstring(responce2.text)
                # выделяем один блок и его кошмарим
                articl_xpath = articl_dom.xpath("//div[contains(@class, 'topic-page__container')]")

                try:
                    time = articl_xpath[0].xpath(".//time[contains(@class, 'topic-header__time')]/text()")[0]
                except:
                    time = ''

                try:
                    author = articl_xpath[0].xpath(".//a[contains(@class, 'topic-authors__author')]/text()")[0]
                except:
                    author = ''
                # Если текста на начальной странице нет, вытащить заголовок со страницы по ссылке.
                if len(text) == 0:
                    try:
                        text = articl_xpath[0].xpath(".//h1/span[contains(@class, 'topic-header__title')]/text()")[0]
                    except:
                        text = ''
                else:
                    text = text[0]
                data_item['text'] = text
                data_item['time'] = time
                data_item['author'] = author
                data_item['link'] = link
                data_item['hash'] = create_hash(data_item, 'text')
                # Если есть пустые строки Автора и Текста, не вносить в общий список
                if len(data_item['author']) != 0 and len(data_item['text']) != 0 and len(data_item['time']) != 0:
                    data_lenta.append(data_item)
                    # функция вставки словаря в базу
                    mongo_add(dblenta, data_item)
                sleep(0.5)
        pprint(data_lenta)
        print(len(data_lenta))
        print()


def create_hash(dict, str_key):
    """ создание хеша по одному ключу из словаря. Возвращает хеш или None
        # TODO есть зацепка, что свои хеши уже есть в Mondo.
    """
    try:
        hash = (str(dict[str_key])).encode()
    except:
        print(f'ERROR!! {str_key}:{dict[str_key]}.')
        return None
    else:
        index_hash = hashlib.md5(hash).hexdigest()
        return index_hash


def mongo_create_dict():
    """ Создание базы данных и коллекции. Запускается из main единожды перед основной функцией. Возвращает коллекцию """
    client = MongoClient('127.0.0.1', 27017)  # подключились к серверу
    db = client['vacancies_hh']  # создали базу
    dblenta = db.dblenta  # создали коллекцию
    # TODO не нравится, что при повторном запуске, опять ключ делается индексом. Сделать позже проверку на существование индекса.
    dblenta.create_index('hash', unique=True)
    return dblenta


def mongo_add(collection_db, dict):
    try:
        collection_db.insert_one(dict)
    except dke:
        print(f"ERROR! Документ с id={dict['_id']} уже существует!")
    else:
        print(f"OK! Документ с id={dict['_id']} внесен в базу!")


if __name__ == '__main__':
    db_lenta = mongo_create_dict()
    crawler_lenta(db_lenta)
    print('='*20)
    for doc in db_lenta.find({}):
        pprint(doc)
    # TODO сделать опрос методом Mongo на предмет сколько всего документов в текущей коллекции. Пока не знаю как
    print()  # для дебагинка
