# -*- coding: utf-8 -*-

# Процесс работы над чем-то (над объектом). Обработка собранных данных.
# Класс и метод работают автоматически. Вызывать их не нужно.

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        clent = MongoClient('localhost', 27017)
        self.mongobase = clent.vacancy_220122

    def process_item(self, item, spider):
        """
        Обрабатываем данные от пауков
        Метод должен определять, какой паук его вызывает, что бы выполнять соответствующую обработку
        """
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['salary_cur'] = self.process_salary_hh(item['salary'])
        elif spider.name == 'sjru':
            item['salary_min'], item['salary_max'], item['salary_cur'] = self.process_salary_sj(item['salary'])
        else:
            print('ПАУК НЕ ОПРЕДЕЛЕН!')
        # del item['salary'] # оставляем переменную для ручной диагностики

        collection = self.mongobase[spider.name]
        if not collection.find_one(item):
            collection.insert_one(item)
        return item

    def del_spaces(self, new_string):
        if '\xa0' in new_string:
            try:
                new_string = new_string.replace('\xa0', '')
                return new_string
            except Exception as e:
                print(e, " ошибка преобразования строки в число.")
        if ' ' in new_string:
            try:
                new_string = new_string.replace(' ', '')
                return new_string
            except Exception as e:
                print(e, " ошибка преобразования строки в число.")

    def process_salary_hh(self, salary):
        """
        Логика обработки зарплаты
        Получаем разный список. Логика поиска:
        1. Ищем текст "от ", находим его номер в списке, номер+1 = ЗП "от";
        2. Аналогично "до ";
        3. Аналогично ищем валюту по тексту с пробелом " ";
        4. Принцип получения ЗП пока игнорируем;
        5. Если поиск по соотв. полям не дал результат, вписываем туда None.
        6. Можно сделать логическую проверку, если сумм нет, то и валюты не должно быть
        """
        if "от " in salary:
            salary_min = salary[salary.index("от ") + 1]
            salary_min = int(self.del_spaces(salary_min))
        else:
            salary_min = None
        if " до " in salary:
            salary_max = salary[salary.index(" до ") + 1]
            salary_max = int(self.del_spaces(salary_max))
        else:
            salary_max = None
        if " " in salary:
            salary_cur = salary[salary.index(" ") + 1]
            if len(salary_cur) <= 1:
                salary_cur = None
        else:
            salary_cur = None

        return salary_min, salary_max, salary_cur


    def process_salary_sj(self, salary):
        """
        Логика обработки зарплаты
        Получаем разный список. Логика поиска:
            list[5]
        1. Если начало "от", то третий элемент тектовое представление ЗП с рублями; запись в 0: ['от', '\xa0', '70\xa0000\xa0руб.', '/', 'месяц']
        2. Если начало "до", то третий элемент тектовое представление ЗП с рублями; запись в 1: ['до', '\xa0', '85\xa0000\xa0руб.', '/', 'месяц']
        3. Есть еще один варинат, где фиксированная ЗП: ["95 000", " ", "руб.", "/", "месяц"]
            list[1]
        4. Если 'По договоренности', то 0,1,2 - None: ['По договорённости']
            list[9]
        5. Остается сложный вариант: ['50\xa0000', '\xa0', '—', '\xa0', '60\xa0000', '\xa0', 'руб.', '/', 'месяц']
        """
        if len(salary) == 5:
            if salary[0] == 'от':
                salary_min = int(self.del_spaces(salary[2])[:-4])
                salary_max = None
                salary_cur = salary[2][-4:]
            elif salary[0] == 'до':
                salary_min = None
                salary_max = int(self.del_spaces(salary[2])[:-4])
                salary_cur = salary[2][-4:]
            else:
                salary_min = int(self.del_spaces(salary[0]))
                salary_max = int(self.del_spaces(salary[0]))
                salary_cur = salary[2]
        elif len(salary) == 1:
            if salary[0] == 'По договорённости':
                salary_min = None
                salary_max = None
                salary_cur = None
            else:
                print('НОВЫЙ ФОРМАТ ЗП: ', salary)
                salary_min = None
                salary_max = None
                salary_cur = None
        elif len(salary) == 9:
            salary_min = int(self.del_spaces(salary[0]))
            salary_max = int(self.del_spaces(salary[4]))
            salary_cur = salary[6]
        else:
            print('НОВЫЙ ФОРМАТ ЗП: ', salary)
            salary_min = None
            salary_max = None
            salary_cur = None

        return salary_min, salary_max, salary_cur
