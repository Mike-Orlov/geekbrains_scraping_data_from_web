# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline

class LeroyMerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost',27017)
        self.mongo_base = client.leroy_merlin

    def process_item(self, item, spider):
        item['features'] = dict(zip(item['features_name'], item['features_value']))        
        del item['features_name']
        del item['features_value']

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

# Для хранения фото по раздельным папкам для каждого объекта переопределить метод file_path  
#    def file_path(self, request, response=None, info=None):
#
#        return 0

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item