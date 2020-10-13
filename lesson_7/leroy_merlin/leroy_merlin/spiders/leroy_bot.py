import scrapy
from scrapy.http import HtmlResponse
from leroy_merlin.items import LeroyMerlinItem
from scrapy.loader import ItemLoader


class LeroyBotSpider(scrapy.Spider):
    name = 'leroy_bot'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response:HtmlResponse):
        items_links = response.xpath("//a[@class='plp-item__info__title']")
        for link in items_links:
            yield response.follow(link, callback=self.parse_items)
        
        next_page = response.xpath("//a[@class='paginator-button next-paginator-button']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_items(self, response:HtmlResponse):
        loader = ItemLoader(item=LeroyMerlinItem(), response=response)
        loader.add_xpath('article', "//span[@slot='article']/@content")
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photo', "//img[@alt='product image']/@data-origin")
        loader.add_xpath('features_name', "//div[@class='def-list__group']/dt/text()")
        loader.add_xpath('features_value', "//div[@class='def-list__group']/dd/text()")
        loader.add_value('link', response.url)
        yield loader.load_item()
