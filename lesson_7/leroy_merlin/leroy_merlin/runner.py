from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

#from leroy_merlin import settings
#from leroy_merlin.spiders.leroy_bot import LeroyBotSpider
from leroy_merlin import settings
from leroy_merlin.spiders.leroy_bot import LeroyBotSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroyBotSpider,search='запорная арматура')

    process.start()