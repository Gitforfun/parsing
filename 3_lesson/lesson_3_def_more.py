#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
from pymongo import MongoClient


def more_salary():
    """
    Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше
    введённой суммы (необходимо анализировать оба поля зарплаты).
    """
    client = MongoClient('127.0.0.1', 27017)  # подключились к серверу
    db = client['vacancies_hh']  # создали/открыли базу
    engineers = db.engineers  # создали коллекцию
    match_list = []

    while True:
        my_salary = input('Введите желаемую ЗП: ')
        try:
            my_salary = int(my_salary)
        except:
            print("Вы ввели нечисловое значение!")
        else:
            break

    for doc in engineers.find({}):
        if doc['salary'][2] == 'руб.':  # если ЗП в рублях
            if doc['salary'][0] and not doc['salary'][1]:  # есть только мин
                if my_salary > doc['salary'][0]:  # если больше мин
                    match_list.append(doc)
            elif doc['salary'][1]:
                if my_salary < doc['salary'][1]:  # если маньше макс
                    match_list.append(doc)
            else:
                pass  # если неудовлетворяет, пропускаем
    pprint(match_list)


if __name__ == '__main__':
    more_salary()
