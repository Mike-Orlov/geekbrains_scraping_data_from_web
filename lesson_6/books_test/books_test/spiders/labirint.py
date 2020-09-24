import scrapy
from scrapy.http import HtmlResponse
from books_test.items import BooksTestItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    query = 'python'
    start_urls = [f'https://www.labirint.ru/search/{query}/?stype=0']

    def parse(self, response:HtmlResponse):
        books = response.xpath('//a[@class="product-title-link"]/@href').extract()
        for book in books:
            yield response.follow(book, callback=self.book_parse)

        next_page = response.xpath("//a[@class='pagination-next__text']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response:HtmlResponse):
        book_link = response.url
        book_name = response.xpath("//h1/text()").extract_first()
        book_authors = response.xpath("//a[@data-event-label='author']/text()").extract()
        book_price_main = response.xpath("//span[@class='buying-priceold-val-number']/text()").extract()
        book_price_sale = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract()
        book_rating = response.xpath("//div[@id='rate']/text()").extract_first()

        yield BooksTestItem(book_link=book_link, book_name=book_name, book_authors=book_authors, 
            book_price_main=book_price_main, book_price_sale=book_price_sale, book_rating=book_rating)