# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re
#re.sub('\D', '', 'aas30dsa20')
class BooksTestPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books_test

    def process_item(self, item, spider):
        if item['book_price_main']:
            item['book_price_main'] = int(re.sub('\D', '', item['book_price_main'][0].split(' ')[0]))
        else:
            item['book_price_main'] = None
        if item['book_price_sale']:
            item['book_price_sale'] = int(re.sub('\D', '',item['book_price_sale'][0]))
        else:
            item['book_price_sale'] = None
        if item['book_rating']:
            item['book_rating'] = item['book_rating'][0]
        else:
            item['book_rating'] = None

        collection = self.mongo_base[spider.name] # Коллекция по имени паука для удобства
        collection.insert_one(item)
        return item
