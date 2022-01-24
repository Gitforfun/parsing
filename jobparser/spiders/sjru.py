# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vakansii/inzhener-po-svarke.html']

    def parse(self, response: HtmlResponse):
        # Рекурсия по поиску следующих страниц
        next_page = response.xpath("//a[contains(@class,'f-test-button-dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        # Поиск всех ссылок на вакансии, переход на них в отдельном потоке с использованием follow (подобие get)
        links = response.xpath("//div[contains(@class,'f-test-vacancy-item')]//span[not(contains(@class,'f-test-text-vacancy-item-company-name'))]/a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # Парсим данные по вновь полученной ссылке. Responce обновляется. Только получаем данные. Не обрабатываем.
        # Обработка данных будет в pipelines для параллельной работы паука
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//h1/following-sibling::span//text()").getall()
        url = response.url
        # Записываем необработанные данные в специализированный объект для полученных данных
        yield JobparserItem(name=name, salary=salary, url=url)  # рекомендация разработчиков, не return
