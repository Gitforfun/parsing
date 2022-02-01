# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import hashlib


class InstaparserPipeline:
    def __init__(self):
        clent = MongoClient('localhost', 27017)
        self.mongobase = clent.instagram

    def process_item(self, item, spider):
        collection = self.mongobase['follows_2']
        item['_id'] = self.create_hash(item)
        if not collection.find_one(item):
            try:
                collection.insert_one(item)
            except Exception as e:
                print(f'ОШИБКА ВНЕСЕНИЯ В БАЗУ: {e}')
            else:
                print(f'ВНЕСЕНО В БАЗУ: {item["owned_user_name"]} {item["friends_group"]} {item["user_name"]}')
        else:
            print(f'УЖЕ ИМЕЕТСЯ: {item["owned_user_name"]} {item["friends_group"]} {item["user_name"]}')
        return item

    def create_hash(self, item):
        """ т.к. id пользователя может быть и в подписках и в подписчиках,
        но не может быть два раза одновременно в одной из групп,
        формируем хеш на основе группы и id "друга".
        hash=hashlib.md5(str_hash.encode()).hexdigest()
        """
        try:
            str_hash = (str(item['friends_group']) + str(item['user_id'])).encode()
        except Exception as e:
            print(f'ERROR!! {e}: {item["friends_group"]}:{item["user_id"]}.')
            return None
        else:
            index_hash = hashlib.md5(str_hash).hexdigest()
            return index_hash
