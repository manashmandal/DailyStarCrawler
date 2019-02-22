import scrapy
from pymongo import MongoClient
import datetime
import logging

class DailyStarSpider(scrapy.Spider):
    name='ds'

    def start_requests(self, start_date="01-09-2007", end_date=None):
        self.baseurl = "https://www.thedailystar.net"
        self.start_url = f"https://www.thedailystar.net/newspaper?date={start_date}"

        self.start_date = datetime.datetime.strptime(start_date, "%d-%M-%Y")
        
        if end_date is None:
            self.end_date = self.start_date + datetime.timedelta(days=1)
            
        else:
            self.end_date = datetime.datetime.strptime(end_date, "%d-%M-%Y")

        # Selectors
        self.GRAB_ALL_NEWS_LINKS = "//h5/a/@href" # extract()

        yield scrapy.Request(url=self.start_url, callback=self.news_iterator)


    def news_iterator(self, response):
        news_links_on_this_page = response.xpath(self.GRAB_ALL_NEWS_LINKS).extract()

        for link in news_links_on_this_page:
            yield scrapy.Request(url=self.baseurl + link, callback=self.news_parser)

        

    def news_parser(self, response):
        logging.info(response.url)