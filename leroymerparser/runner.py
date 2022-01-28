from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerparser import settings
from leroymerparser.spiders.leroymerlin import LeroymerlinSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # search = input('')
    search = 'выключатели%20legrand'
    # process.crawl(LeroymerlinSpider)
    process.crawl(LeroymerlinSpider, search)

    process.start()
