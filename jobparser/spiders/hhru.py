# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']  # ограничитель, паук не пойдет на внешние ссылки. При этом ошибки не будет
    start_urls = ['https://tver.hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&excluded_text=&fromSearchLine=true&text=%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3+%D1%81%D0%B2%D0%B0%D1%80%D0%BA%D0%B0',
                  'https://tver.hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&fromSearchLine=true&text=%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3+%D1%81%D0%B2%D0%B0%D1%80%D0%BA%D0%B0'
                  ]

    def parse(self, response: HtmlResponse):
        # Рекурсия по поиску следующих страниц
        next_page = response.xpath("//a[data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        # Поиск всех ссылок на вакансии, переход на них в отдельном потоке с использованием follow (подобие get)
        links = response.xpath("//span/a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # Парсим данные по вновь полученной ссылке. Responce обновляется. Только получаем данные. Не обрабатываем.
        # Обработка данных будет в pipelines для параллельной работы паука
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//div[@data-qa='vacancy-salary']//text()").getall()
        url = response.url
        # Записываем необработанные данные в специализированный объект для полученных данных
        yield JobparserItem(name=name, salary=salary, url=url)  # рекомендация разработчиков, не return

