# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # Необходимо заранее прописать все данные, которые будут сохраняться и использоваться, включая обработанные
    # define the fields for your item here like:
    name = scrapy.Field()  # должность
    salary = scrapy.Field()  # объект,типа словаря, с грязными данными о зарплате
    url = scrapy.Field()  # ссылка на вакансию
    salary_min = scrapy.Field()  # минимальная ЗП
    salary_max = scrapy.Field()  # максимальная ЗП
    salary_cur = scrapy.Field()  # валюта
    _id = scrapy.Field()  # идентификатор для Монго. Иначе Монго не примет item
    # hash = scrapy.Field()  # хеш проверка на дубликат
