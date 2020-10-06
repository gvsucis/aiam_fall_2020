import scrapy
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
from ..items import TutorialItem


class QuoteSpider(scrapy.Spider):
    name = "quotess"
    page_number = 2
    start_urls = [
        "http://quotes.toscrape.com/login"
    ]
    
    def parse(self, response):
        token = response.css('form input::attr(value)').get()
        return FormRequest.from_response(response, formdata={
            'csrf_token': token,
            'username': 'username',
            'password': 'password'
        }, callback=self.start_scraping)

    def start_scraping(self, response):
        open_in_browser(response)
        items = TutorialItem()

        all_div_quotes = response.css('div.quote')


        for quote in all_div_quotes:
            title = quote.css('span.text::text').extract()
            author = quote.css('.author::text').extract()
            tags = quote.css('.tag::text').extract()
            
            items['title'] = title
            items['author'] = author
            items['tags'] = tags
            
            yield items

        next_page = 'http://quotes.toscrape.com/page/'+ str(QuoteSpider.page_number)+'/'
        if QuoteSpider.page_number < 11:
            QuoteSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse)