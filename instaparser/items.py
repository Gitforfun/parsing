# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()  # образец

    friends_group = scrapy.Field()
    owned_user_name = scrapy.Field()
    owned_user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    user_pic = scrapy.Field()
    _id = scrapy.Field()

