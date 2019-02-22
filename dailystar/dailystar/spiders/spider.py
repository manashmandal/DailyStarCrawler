import scrapy
from pymongo import MongoClient
import datetime

class DailyStarSpider(scrapy.Spider):
    name='ds'

    def start_requests(self, start_date="01-09-2007", end_date=""):
        self.start_url = f"https://www.thedailystar.net/newspaper?date={start_date}"

        yield scrapy.Request(url=self.start_url, callback=self.news_iterator)


    def news_iterator(self, response):
        pass


    def news_parser(self, response):
        pass