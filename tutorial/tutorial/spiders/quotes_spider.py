import scrapy 
from ..items import TutorialItem
class QuoteSpider(scrapy.Spider):
    name = "quotes"

    start_urls = [
        "http://quotes.toscrape.com/"
    ]
    
    def parse(self, response):

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