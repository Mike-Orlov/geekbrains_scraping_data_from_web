# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksTestItem(scrapy.Item):
    # define the fields for your item here like:
    book_link = scrapy.Field()
    book_name = scrapy.Field()
    book_authors = scrapy.Field()
    book_price_main = scrapy.Field()
    book_price_sale = scrapy.Field()
    book_rating = scrapy.Field()
    # т.к. Mongo автоматом создает _id, то если не объявить у класса этот атрибут, 
    # то загрузка в БД из модуля Pipeline не произойдет
    _id = scrapy.Field()