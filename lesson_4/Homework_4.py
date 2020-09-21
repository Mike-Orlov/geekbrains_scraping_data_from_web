from pprint import pprint
from lxml import html
import pandas as pd
import requests
import datetime
import time
from pymongo import MongoClient
import pymongo
from hashlib import md5

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/84.0.4147.135 Safari/537.36'}

lenta_link = 'https://lenta.ru'
mail_link = 'https://news.mail.ru'
yandex_link = 'https://yandex.ru/news'

def yandex_news_parser():
    response = requests.get(yandex_link, headers=headers)
    dom = html.fromstring(response.text)

    all_blocks = dom.xpath("//article")

    articles_yandex = []

    for block in all_blocks:
        article = {}
        site_name = 'yandex'
        source_name = block.xpath(".//span[@class='mg-card-source__source']//text()")[0]
        article_name = block.xpath(".//h2/text()")[0]
        article_link = block.xpath(".//a[@class='news-card__link']/@href")[0]
        if 'Вчера' in block.xpath(".//span[contains(@class, 'source__time')]/text()")[0]:
            article_date = block.xpath(".//span[contains(@class, 'source__time')]/text()")[0].split(' ')[1] + ', ' + str(datetime.datetime.now().date() - datetime.timedelta(days=1))
        else:
            article_date = block.xpath(".//span[contains(@class, 'source__time')]/text()")[0] + ', ' + str(datetime.datetime.now().date())
        
        article['source_name'] = source_name
        article['site_name'] = site_name
        article['article_name'] = article_name
        article['article_link'] = article_link
        article['article_date'] = article_date

        articles_yandex.append(article)
    return(articles_yandex)

def lenta_news_parser():
    response = requests.get(lenta_link, headers=headers)
    dom = html.fromstring(response.text)

    all_blocks = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[@class='item'] | \
                            //section[@class='row b-top7-for-main js-top-seven']//div[@class='first-item']")

    articles_lenta = []

    for block in all_blocks:
        article = {}
        site_name = 'lenta'
        source_name = 'Lenta.ru'
        article_name = block.xpath(".//text()")[1].replace('\xa0', ' ')
        article_link = lenta_link + block.xpath(".//a/@href")[0]
        article_date = block.xpath(".//time/@datetime")[0]

        article['source_name'] = source_name
        article['site_name'] = site_name
        article['article_name'] = article_name
        article['article_link'] = article_link
        article['article_date'] = article_date

        articles_lenta.append(article)
    return(articles_lenta)

def mail_news_parser():
    response = requests.get(mail_link, headers=headers)
    dom = html.fromstring(response.text)

    all_blocks = dom.xpath("//div[@class='block']//li | //div[@class='block']//div[contains(@class, 'daynews__item')]")

    articles_mail = []

    for block in all_blocks:
        article = {}
        site_name = 'mail'
        if 'http' in block.xpath(".//a/@href")[0]:
            article_link = block.xpath(".//a/@href")[0]
        else:
            article_link = mail_link + block.xpath(".//a/@href")[0]
        mail_response = requests.get(article_link)
        mail_dom = html.fromstring(mail_response.text)
        article_name = mail_dom.xpath("//span[@class='hdr__text']/h1/text()")[0].replace('\xa0', ' ')
        article_date = mail_dom.xpath("//span[@class='note__text breadcrumbs__text js-ago']/@datetime")[0]
        source_name = mail_dom.xpath("//a[contains(@class, 'breadcrumbs__link')]/span/text()")[0]

        article['source_name'] = source_name
        article['site_name'] = site_name
        article['article_name'] = article_name
        article['article_link'] = article_link
        article['article_date'] = article_date

        articles_mail.append(article)
    return(articles_mail)

#pprint(yandex_news_parser()) # Проверка
#pprint(lenta_news_parser())
#pprint(mail_news_parser())

yandex_df = pd.DataFrame(yandex_news_parser())
lenta_df = pd.DataFrame(lenta_news_parser())
mail_df = pd.DataFrame(mail_news_parser())
#print(yandex_df.head())

client = MongoClient('127.0.0.1', 27017) # ip-адресс и порт
db = client['news'] # указатель на БД, сама БД появляется только когда туда записаны какие-то данные (особенность Mongo)

yandex_news = db.yandex_news # создание "коллекции" внутри БД, это как таблица в SQL
mail_news = db.mail_news
lenta_news = db.lenta_news

def update_news_db(new_df_file):
    """
    Функция добавляет в БД новости по 3-м коллекциям в зависимости от сайта. Дубли новостей игнорируются.

    На вход принимает файл в формате pandas dataframe.
    """
    for string in new_df_file.to_dict(orient='records'):
        if string['site_name']=='yandex':
            yandex_news.update_one({'article_link': string['article_link']}, {'$set': string}, upsert=True)
        elif string['site_name']=='mail':
            mail_news.update_one({'article_link': string['article_link']}, {'$set': string}, upsert=True)
        elif string['site_name']=='lenta':
            lenta_news.update_one({'article_link': string['article_link']}, {'$set': string}, upsert=True)

update_news_db(yandex_df)
update_news_db(lenta_df)
update_news_db(mail_df)

yandex_news.create_index([('article_date', pymongo.ASCENDING)]) # Сделаем также индексы
mail_news.create_index([('article_date', pymongo.ASCENDING)])
lenta_news.create_index([('article_date', pymongo.ASCENDING)])

for news in yandex_news.find({}): # Проверка содержания
    pprint(news)

print(yandex_news.count_documents({})) # Проверка колличества
print(mail_news.count_documents({}))
print(lenta_news.count_documents({}))

#yandex_news.delete_many({})
#mail_news.delete_many({})
#lenta_news.delete_many({})