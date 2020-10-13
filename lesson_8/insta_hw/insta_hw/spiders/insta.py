import scrapy
from scrapy.http import HtmlResponse
from insta_hw.items import InstaHwItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy

class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = 'gbinsta_test'
    insta_password = '#PWD_INSTAGRAM_BROWSER:10:1601724092:ASJQAKkKm6/EozMnxydq3K1y4UF1GpurGY+l6ANRaAskPNAX2R18wFsXBr8aFJ1AxrMI1opG9pzsSrwjVdDnnaZIZIuK/uFlc3lAQZRoMX4cP9rCwbvJwb8Lor5LJ8E/YJhFjCBtGP5/KGnJ'
    login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['mazur__alex', 'kirill_007']   #Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'  #graphql - метод работы некоторых вэб-приложений, браузер шлет запросы в одну точку с параметрами урла query_hash и переменными, что чем-то похоже на запросы к недокументированному API
    #hash для получения данных о фолловерах. Передается в параметр query_hash и для каждой цели запроса своё значение.
    hash_dict = {'followers_hash':'c76146de99bb02f6415203be841dd25a','following_hash':'d04b0a864b4b54837c0d870b0e77e076'}

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)       #csrf token забираем из html
        yield scrapy.FormRequest(          #заполняем форму для авторизации
            self.login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username':self.insta_login, 'enc_password':self.insta_password},
            headers={'X-CSRFToken':csrf_token}
        )
    
    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:                 #Проверяем ответ после авторизации
            for user in self.parse_users:
                yield response.follow(                  #Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{user}',              #Только метод follow сохраняет сессию, поэтому пользуемся дальше им
                    callback= self.followers_following_lists,
                    cb_kwargs={'username':user}
                )
    
    def followers_following_lists(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       #Получаем id пользователя
        variables = {'id':user_id,                                    #Формируем словарь для передачи даных в запрос
                    'first':24}                                      #24 первых выводится                                      
        for key, query_hash in self.hash_dict.items():
            link_to_parse = f'{self.graphql_url}query_hash={query_hash}&{urlencode(variables)}'    #Формируем ссылку для получения данных о подписчиках или подписках (urlencode для удобства обработки словаря)
            yield response.follow(
                link_to_parse,
                callback=self.user_followers_following_parse,
                cb_kwargs={'username':username,
                        'user_id':user_id,
                        'variables':deepcopy(variables),     #variables ч/з deepcopy во избежание гонок (когда данные по нескольким юзерам собираются, процессы хватают чужие variables)
                        'target':deepcopy(key)}         # !! Попробовал дипкопи тоже
            )

    def user_followers_following_parse(self, response:HtmlResponse, username, user_id, variables, target): #Принимаем ответ. Не забываем про параметры от cb_kwargs 
        j_data = json.loads(response.text)

        if target == 'followers_hash':
            target_j_data = j_data.get('data').get('user').get('edge_followed_by')
            friend_type = 'follower'
        elif target == 'following_hash':
            target_j_data = j_data.get('data').get('user').get('edge_follow')
            friend_type = 'following'
        print()
        page_info = target_j_data.get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables = {'id':user_id,                                    #Формируем словарь для передачи даных в запрос
                        'first':24}                                      #24 первых выводится
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            link_to_parse = f'{self.graphql_url}query_hash={self.hash_dict[target]}&{urlencode(variables)}'
            yield response.follow(
                link_to_parse,
                callback=self.user_followers_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'target': target}
            )
        
        friends = target_j_data.get('edges')     #Сами друзья
        for friend in friends:                   #Перебираем друзей, собираем данные
            item = InstaHwItem(
                user_id = user_id,
                user_name = username,
                friend_type = friend_type,
                friend_id = friend['node']['id'],
                friend_username = friend['node']['username'],
                friend_full_name = friend['node']['full_name'],
                friend_photo = friend['node']['profile_pic_url'],
                #friend_raw_data = friend['node']
            )
            yield item                  #В пайплайн

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')    