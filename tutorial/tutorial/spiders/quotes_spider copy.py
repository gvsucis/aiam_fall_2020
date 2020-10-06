import scrapy 
from ..items import TutorialItem
class QuoteSpider(scrapy.Spider):
    name = "quotes"
    page_number = 2
    start_urls = [
        "http://quotes.toscrape.com/page/1/"
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

        next_page = 'http://quotes.toscrape.com/page/'+ str(QuoteSpider.page_number)+'/'
        if QuoteSpider.page_number < 11:
            QuoteSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse)