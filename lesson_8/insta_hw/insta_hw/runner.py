from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from insta_hw.spiders.insta import InstaSpider
from insta_hw import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider)
    
    process.start()