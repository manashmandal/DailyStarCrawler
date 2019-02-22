import scrapy
from pymongo import MongoClient
import datetime
import logging
from scrapy.exceptions import CloseSpider
from string import punctuation, digits

punct_remover = str.maketrans('', '', punctuation + digits)

FILTER_KEYWORDS="""fire
blast
burnt
burn
burns
explosion
inferno
blaze
fire""".split('\n')

logging.info(FILTER_KEYWORDS)


# Get the collection
news = MongoClient(connect=False)['dailystar']['news']

class DailyStarSpider(scrapy.Spider):
    name='ds'

    # First date - 01-09-2007
    def start_requests(self, start_date="22-02-2019", end_date="22-02-2019"):
        self.baseurl = "https://www.thedailystar.net"
        self.start_url = f"https://www.thedailystar.net/newspaper?date={start_date}"

        self.start_date = datetime.datetime.strptime(start_date, "%d-%m-%Y")
        self.current_date = self.start_date

        self.date_margin = 10
        
        if end_date is None:
            self.end_date = self.start_date + datetime.timedelta(days=1)
            
        else:
            self.end_date = datetime.datetime.strptime(end_date, "%d-%m-%Y")

        # Selectors
        self.GRAB_ALL_NEWS_LINKS = "//h5/a/@href//text()/../@href" # extract()
        self.GRAB_ALL_NEWS_TITLE = "//h5/a//text()" # extract()
        self.GRAB_NEWS_BODY = "//div[contains(@class,'field-body')]//p/text()" # extract()
        self.GRAB_REPORTER = "//span[@itemprop='name']/text()" # extract()
        self.GRAB_REPORTERS = "//span[@itemprop='name']/a/text()" # extract()
        self.GRAB_BREADCRUMB = "//div[@class='breadcrumb']//span[@itemprop='name']/text()"
        self.GRAB_TITLE = "//h1[@itemprop='headline']//text()"


        yield scrapy.Request(url=self.start_url, callback=self.news_iterator)


    def news_iterator(self, response):
        news_links_on_this_page = response.xpath(self.GRAB_ALL_NEWS_LINKS).extract()
        news_title_on_this_page = response.xpath(self.GRAB_ALL_NEWS_TITLE).extract()

        # assert len(news_links_on_this_page) == len(news_title_on_this_page)

        for idx, link in enumerate(news_links_on_this_page):
            
            # Remove punctuations after getting the title
            title = news_title_on_this_page[idx].lower().translate(punct_remover)

            logging.info("TITLE " + title)

            scrap_it = False
            # If condition matches then yield result 
            for keyword in FILTER_KEYWORDS:
                logging.info(title)
                if keyword in title:
                    scrap_it = True
            
            if scrap_it:
                request = scrapy.Request(url=self.baseurl + link, callback=self.news_parser)
                request.meta['date_published'] = self.current_date
                yield request

        self.current_date = self.current_date + datetime.timedelta(days=1)

        if self.current_date > ( self.end_date + datetime.timedelta(days=self.date_margin) ):
            raise CloseSpider("Current date - {} - end Date - {}".format(
                self.current_date.strftime("%d-%m-%Y"), self.end_date.strftime("%d-%m-%Y")
            ))

        yield scrapy.Request(self.baseurl + '/newspaper?date=' + self.current_date.strftime("%d-%m-%Y"), callback=self.news_iterator)

    def news_parser(self, response):
        date_published = response.meta['date_published']
        permalink = response.url
        body_text = " ".join(text.strip() for text in response.xpath(self.GRAB_NEWS_BODY).extract())
        reporter = response.xpath(self.GRAB_REPORTER).extract()
        title = response.xpath(self.GRAB_TITLE).extract_first() or ""
        breadcrumb = response.xpath(self.GRAB_BREADCRUMB).extract()

        # if first grabber fails try using the next one
        if reporter == []:
            reporter = response.xpath(self.GRAB_REPORTERS).extract()

        data = dict(
            title=title,
            breadcrumb=breadcrumb,
            date_published=date_published,
            news_body=body_text,
            reporter=reporter,
            permalink=permalink
        )

        news.update_one({ 'permalink' : permalink }, {"$set" : data } , upsert=True)


        