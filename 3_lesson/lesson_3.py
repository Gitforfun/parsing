#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
from time import sleep  # добавил для избежания бана. Возможно не актуально, всвязи с медленной работы супа
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
import hashlib


def separator_salaries(string_salaries):
    """ процедура для разделения текстового представления ЗП на список [мин, макс, валюта]"""
    salary = [None, None, None]
    if string_salaries:
        item_sep = string_salaries.split(' ')
        # print(item_sep)
        if item_sep[0] == 'от':
            sum_str = item_sep[1].split('\u202f')
            salary[0] = int(sum_str[0] + sum_str[1])
        elif item_sep[0] == 'до':
            sum_str = item_sep[1].split('\u202f')
            salary[1] = int(sum_str[0] + sum_str[1])
        else:
            sum_str1 = item_sep[0].split('\u202f')
            sum_str2 = item_sep[2].split('\u202f')
            salary[0] = int(sum_str1[0] + sum_str1[1])
            salary[1] = int(sum_str2[0] + sum_str2[1])
        salary[-1] = item_sep[-1]
    return salary


def separator_employer(string_employer):
    """
    процедура для замены спецсимвола '\xa0' на пробел между формой и наименованием организации
    Позже понял, что это пробел, но неразрывный. И Монго его опять вставляет. Можно убрать эту функцию.
    """
    try:
        string_employer.replace('\xa0', ' ')
    except:
        pass
    return string_employer


def create_hash(dict, str_1, str_2):
    """ создание хеш, по двум ключам из словаря. Возвращает хеш или None """
    try:
        hash = (str(dict[str_1]) + str(dict[str_2])).encode()
    except:
        print(f'ERROR!! {str_1}:{dict[str_1]}, {str_2}:{dict[str_2]}.')
        return None
    else:
        index_hash = hashlib.md5(hash).hexdigest()
        return index_hash


def mongo_create():
    """ Создание базы данных и коллекции. Запускается из main единожды перед основной функцией. Возвращает коллекцию """
    client = MongoClient('127.0.0.1', 27017)  # подключились к серверу
    db = client['vacancies_hh']  # создали базу
    engineers = db.engineers  # создали коллекцию
    # engineers.create_index([('hash', pymongo.HASHED)], name='uniq_index', unique=True)  # создаем индексированную
    # пару для кеша
    # TODO не нравится, что при повторном запуске, опять ключ делается индексом. Сделать проверку на
    #  существование индекса.
    engineers.create_index('hash', unique=True)
    return engineers


def mongo_add(collection_db, dict):
    try:
        collection_db.insert_one(dict)
    except dke:
        print(f"ERROR! Документ с id={dict['_id']} уже существует!")


def crawler_hh(engineers):
    """ Основное тело программы. Оставил фрагменты кода для записи данных в json"""
    main_url = 'https://hh.ru'
    add_url = '/search/vacancy/'
    page = 0
    params = {'area': 1, 'fromSearchLine': 'true', 'text': 'технолог сварка', 'customDomain': 1, 'page': page}
    filename = 'vacancies.json'
    vacancies_list = []
    permit = True  # флаг для повторения цикла

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

    while permit:
        response = requests.get(main_url + add_url, params=params, headers=headers)

        if response.ok:
            dom = bs(response.text, 'html.parser')
            vacancies = dom.find_all('div', {
                'class': 'vacancy-serp-item'})  # , 'data-qa': 'vacancy-serp__vacancy' vacancy-serp-item-body__main-info

            for vacancy in vacancies:
                vacancy_data = {}
                info = vacancy.find('a', {'class': 'bloko-link'})  # 'data-qa': 'vacancy-serp__vacancy-title'
                profession = info.text
                prof_link = info.get('href')
                salary_info = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"})
                employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text
                try:
                    salary = salary_info.text
                except:
                    salary = None

                vacancy_data['profession'] = profession
                vacancy_data['employer'] = separator_employer(employer)
                vacancy_data['salary'] = separator_salaries(salary)
                vacancy_data['link'] = prof_link
                vacancy_data['url'] = main_url
                vacancy_data['hash'] = create_hash(vacancy_data, 'profession', 'employer')

                #TODO сюда добавить функцию вставки словаря в базу
                mongo_add(engineers, vacancy_data)

                # старый код для формирования базы для json
                vacancies_list.append(vacancy_data)

                # print()  # для дебагинка

            # флаг для завершения перехода на следующую страницу
            if not dom.find('div', {'data-qa': 'pager-block'}).find('a', {'data-qa': 'pager-next'}):
                permit = False

        params['page'] += 1
        sleep(0.5)


    # временно закоментил формирование файла
    # with open(filename, "w", encoding='utf-8') as file:
    #     json.dump(vacancies_list, file, ensure_ascii=False)
    # pprint(vacancies_list)


if __name__ == '__main__':
    db_engineers = mongo_create()
    crawler_hh(db_engineers)
    print()  # для дебагинка
