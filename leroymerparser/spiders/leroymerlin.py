import scrapy
from scrapy.http import HtmlResponse
from leroymerparser.items import LeroymerparserItem
from scrapy.loader import ItemLoader  # класс промежуточной легкой обработки данных


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    # start_urls = ['https://leroymerlin.ru/search/?q=%D0%B2%D1%8B%D0%BA%D0%BB%D1%8E%D1%87%D0%B0%D1%82%D0%B5%D0%BB%D0%B8%20legrand']
    # создаем конструктор
    def __init__(self, search):
        # создаем супер инициализацию, чтобы не потерять инициализацию класса, на основе которого создаем текущий
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        # оптимизация кода: не извлекаем текст ссылки из тега <a> @href и не получаем данные .get(). Скрапи сам это делает, видя тег <a>, догадываясь, что работать придется со ссылкой
        # НО! Оптимизация не срабатывает при рекурсии/переходе на следующую станицу! Пришлось вернуть @href и .get()
        # Рекурсия по поиску следующих страниц
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        # Поиск всех ссылок на вакансии, переход на них в отдельном потоке с использованием follow (подобие get)
        links = response.xpath("//a[@data-qa='product-image']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photo', "//source[contains(@srcset, 'w_2000,h_2000')]/@srcset")
        loader.add_value('url', response.url)
        yield loader.load_item()
