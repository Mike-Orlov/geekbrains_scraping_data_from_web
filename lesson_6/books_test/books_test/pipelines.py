# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class BooksTestPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books_test

    def process_item(self, item, spider):
        item['book_price_main'] = int(item['book_price_main'])
        item['book_price_sale'] = int(item['book_price_sale'])
        item['book_rating'] = float(item['book_rating'])

        collection = self.mongo_base[spider.name] # Коллекция по имени паука для удобства
        collection.insert_one(item)
        return item
