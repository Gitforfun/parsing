# -*- coding: utf-8 -*-

import json
import re

import scrapy
from scrapy.http import HtmlResponse  # для типизации responce. Легче работать с подсказками pycharm
from urllib.parse import urlencode  # парсинг и превращение словаря в понятную структуру для сервера
# TODO почитать самостоятельно про urllib.parse urlencode
from instaparser.items import InstaparserItem
from copy import deepcopy  # для передачи копированием (а не ссылочной передачи) переменных в многопоточный метод
from pprint import pprint  # для диагностики


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login_name = 'mailfspm_for_fun'  # '51661541336'
    inst_login_pwd = '#PWD_INSTAGRAM_BROWSER:10:1643399453:AaJQAP+9vgW/YH0vR5e0Jse0+7PttR0Mjuo8CXyxNRRKAwB12NdMBUHZmm3c+qIW6nPFwUCHKixtYp+HDfuqXSUmaRrTO9Kgx98HlTB036xMN3sPG5shk19MZ3jxVszX3KgwFZd5CPe5gQMWjxl1MQ=='

    parse_users = ('mega_klimat', 'zoomag_zhuk')

    friendships_url = 'https://i.instagram.com/api/v1/friendships'  # постоянный фрагмент ссылки на подписки и подписчиков
    count = 12  # стандартная порция загружаемых подльзователей в подписчиках и подписках
    api_headers = {'User-Agent': 'Instagram 155.0.0.37.107'}  # для корректного формирования запроса на показ подписок и подписчиков. Никак не выявляется анализом в браузере


    def parse(self, response: HtmlResponse):  # заранее указывам типизацию респонса
        # прежде чем авторизовыватсья, ищем в полученной начальной страницы инстаграмм, где-то в тексте csrf-токен с помощью re
        csrf = self.fetch_csrf_token(response.text)  # ищем токен
        # отправляем поля формы авторизации, путем другого запроса-POST
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={
                'username': self.inst_login_name,
                'enc_password': self.inst_login_pwd,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'trustedDeviceRecords': "{}"
            },
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()  # забираем в словарь ответ об успешной авторизации в виде json
        if j_body.get('authenticated'):  # проверяем, успешна ли авторизация
            for user in self.parse_users:
                yield response.follow(f'/{user}',  # точка входа. follow вместо get для сохранения сессии
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user}  # дополнительные аргументы при вызыве функции по callback
                                      )
        else:
            print("Авторизация не пройдена")

    def user_data_parse(self, response: HtmlResponse, username):
        """ Получаем request на пользователя под авторизацией.
        Первый запрос без указания номера крайней грани/пользователя!
        Дополнительно передаем имя parse_user с помощью cd_kwargs для дальнейшего использования.
        ВНИМАНИЕ: cb_kwargs передает variables которую ссылочно меняют разные потоки. Необходимо передавать variables
        методом копирования, а не ссылки. Решается методом deepcopy.
        В cb_kwargs и, соответственно, в вызываемой методе важно соблюдать последовательность аргументов.
        Вызывается из login """
        user_id = self.fetch_user_id(response.text, username)
        # формируем стартовую ссылку на подписки
        variables_following = {'count': self.count}
        following_url = f'{self.friendships_url}/{user_id}/following/?{urlencode(variables_following)}'
        # Пример: https://i.instagram.com/api/v1/friendships/3614809675/following/?count=12
        yield response.follow(following_url,
                              callback=self.user_following_parse,
                              cb_kwargs={'username': username, 'user_id': user_id,
                                         'variables_following': deepcopy(variables_following)},
                              headers=self.api_headers
                              )
        # формируем ссылку на подписчиков
        variables_followers = {'count': self.count, 'search_surface': 'follow_list_page', 'max_id': 12}
        followers_url = f'{self.friendships_url}/{user_id}/followers/?{urlencode(variables_followers)}'
        # Пример: 	https://i.instagram.com/api/v1/friendships/3614809675/followers/?count=12&max_id=12&search_surface=follow_list_page
        yield response.follow(followers_url,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username, 'user_id': user_id,
                                         'variables_followers': deepcopy(variables_followers)},
                              headers=self.api_headers
                              )

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables_following):
        """ ПОДПИСКИ """
        j_data = response.json()
        users = j_data.get('users')  # порционный список пользователей
        if j_data['big_list']:
            variables_following['max_id'] = j_data.get('next_max_id')
            following_url = f'{self.friendships_url}/{user_id}/following/?{urlencode(variables_following)}'
            # Пример: https://i.instagram.com/api/v1/friendships/3614809675/following/?count=12
            yield response.follow(following_url,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'username': username, 'user_id': user_id, 'variables': deepcopy(variables_following)},
                                  headers=self.api_headers
                                  )
        # т.к. yield не прерывает скрипт, то тут указываем продолжение: сохранение полученных данных в Item
        for user in users:
            item = InstaparserItem(
                friends_group='following',
                owned_user_name=username,
                owned_user_id=user_id,
                user_name=user.get('username'),
                user_id=user.get('pk'),
                user_pic=user.get('profile_pic_url'),
                _id=''
            )
            yield item


    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables_followers):
        """ ПОДПИСЧИКИ """
        j_data = response.json()
        users = j_data.get('users')  # порционный список пользователей
        if j_data['big_list']:
            variables_followers['max_id'] = j_data.get('next_max_id')
            followers_url = f'{self.friendships_url}/{user_id}/followers/?{urlencode(variables_followers)}'
            # Пример: https://i.instagram.com/api/v1/friendships/3614809675/followers/?count=12&max_id=12&search_surface=follow_list_page
            yield response.follow(followers_url,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username, 'user_id': user_id, 'variables': deepcopy(variables_followers)},
                                  headers=self.api_headers
                                  )
        # т.к. yield не прерывает скрипт, то тут указываем продолжение: сохранение полученных данных в Item
        for user in users:
            item = InstaparserItem(
                friends_group='followers',
                owned_user_name=username,
                owned_user_id=user_id,
                user_name=user.get('username'),
                user_id=user.get('pk'),
                user_pic=user.get('profile_pic_url'),
                _id=''
            )
            yield item

    def fetch_csrf_token(self, text):
        """ Get csrf-token for auth """
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()  # ищем последовательность "csrf_token":"набор символов"
        return matched.split(':').pop().replace(r'"', '')  # разделяем текст на список. Разделитель :. Убираем двойные кавычки. Осталось понять что такое pop().

    def fetch_user_id(self, text, username):
        """ Поиск в responce.text совпанения имени цели в ранее определенной структуре (в коде js)
        и выцепление/возвращения ее id
        ВНИМАНИЕ: Поиск id происходит только если у пользователя-цели есть свои публикации
        """
        try:
            matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
            # matched = re.search('\"id\":\"\\d+\"', text).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"')