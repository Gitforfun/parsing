# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(value):
    try:
        value = value.replace('\xa0', '')
    except:
        pass
    try:
        value = int(value)
    except:
        pass
    finally:
        return value

class LeroymerparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())  # TakeFirst берет первый элемент, как get()
    price = scrapy.Field(input_processor=MapCompose(clear_price), output_processor=TakeFirst())
    url = scrapy.Field()
    photo = scrapy.Field()
