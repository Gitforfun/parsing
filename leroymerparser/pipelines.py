# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os.path
from urllib.parse import urlparse

import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline  # для работы с файлами типа изображений


class LeroymerparserPipeline:
    def process_item(self, item, spider):
        return item

class LeroymerPhotosPipeline(ImagesPipeline):
    """ скласс для работы с изображениями. Наследуемся от встроенного класса в pipelines """
    def get_media_requests(self, item, info):  # точка входа
        if item['photo']:  # если список не пустой
            for img in item['photo']:
                try:  # пытаемся скачать файл. Это не всегда получится
                    yield scrapy.Request(img)  # отдельный запрос/сессия, по которой формируется респонс
                except Exception as e:  # выводим исключение на экран
                    print(e)

    def item_completed(self, results, item, info):  # для операций сразу после скачивания файла
        item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return os.path.join(item['name'], os.path.basename(urlparse(request.url).path))
