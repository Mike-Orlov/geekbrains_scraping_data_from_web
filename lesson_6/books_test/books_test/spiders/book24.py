import scrapy
from scrapy.http import HtmlResponse
from books_test.items import BooksTestItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    query = 'python'
    start_urls = [f'https://book24.ru/search/?q={query}']

    def parse(self, response:HtmlResponse):
        books = response.xpath('//a[contains(@class, "book__title-link")]/@href').extract()
        for book in books:
            yield response.follow(book, callback=self.book_parse)

        next_page = response.xpath('//a[@class="catalog-pagination__item _text js-pagination-catalog-item" and text()="Далее"]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response:HtmlResponse):
        book_link = response.url
        book_name = response.xpath("//h1/text()").extract_first()
        # Намеренно беру только первого автора
        book_authors = response.xpath('//span[@class="item-tab__chars-key" and text()="Автор:"]/../span[@class="item-tab__chars-value"]/a/text()').extract_first()
        book_price_main = response.xpath("//div[@class='item-actions__price-old']/text()").extract()
        book_price_sale = response.xpath("//div[@class='item-actions__price']/b/text()").extract()
        book_rating = response.xpath("//span[@class='rating__rate-value']/text()").extract()

        yield BooksTestItem(book_link=book_link, book_name=book_name, book_authors=book_authors, 
            book_price_main=book_price_main, book_price_sale=book_price_sale, book_rating=book_rating)