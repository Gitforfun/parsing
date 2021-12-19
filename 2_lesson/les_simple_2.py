#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
from time import sleep

main_url = 'https://hh.ru'
add_url = '/search/vacancy/'
page = 0
params = {'area': 1, 'fromSearchLine': 'true', 'text': 'технолог сварка', 'page': page}
filename = 'vacancies.json'
vacancies_list = []
permit = True  # флаг для повторения цикла

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}


def separator_salaries(string_salaries):
    """ процедура для разделения текстового представления ЗП на список [мин, макс, валюта]"""
    salary = [None, None, None]
    if string_salaries:
        salary = [None, None, None]
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
            try:
                salary = salary_info.text
            except:
                salary = None

            vacancy_data['profession'] = profession
            vacancy_data['salary'] = separator_salaries(salary)
            vacancy_data['link'] = prof_link
            vacancy_data['url'] = main_url
            vacancies_list.append(vacancy_data)

        if not dom.find('div', {'data-qa': 'pager-block'}).find('a', {'data-qa': 'pager-next'}):
            permit = False
    params['page'] += 1
    sleep(0.5)

with open(filename, "w", encoding='utf-8') as file:
    json.dump(vacancies_list, file, ensure_ascii=False)
pprint(vacancies_list)
