from lxml import etree, html
import requests
import datetime
from pymongo import MongoClient
from string import punctuation
import asyncio
punct_remover = str.maketrans('', '', punctuation )

class SELECTORS:
    GRAB_ALL_NEWS_LINKS = "//h5/a//text()/../@href" # extract()
    GRAB_ALL_NEWS_TITLE = "//h5/a//text()" # extract()
    GRAB_NEWS_BODY = "//div[contains(@class,'field-body')]//p/text()" # extract()
    GRAB_REPORTER = "//span[@itemprop='name']/text()" # extract()
    GRAB_REPORTERS = "//span[@itemprop='name']/a/text()" # extract()
    GRAB_BREADCRUMB = "//div[@class='breadcrumb']//span[@itemprop='name']/text()"
    GRAB_TITLE = "//h1[@itemprop='headline']//text()"

BASE_URL = "https://www.thedailystar.net"
URL = "https://www.thedailystar.net/newspaper?date="

FILTER_KEYWORDS="""fire
blast
burnt
burn
burns
explosion
inferno
blaze""".split('\n')

news = MongoClient(connect=False)['dailystar']['news']

sd = "01-09-2007"
ed = "31-12-2007"
DATE_FORMATTER = "%d-%m-%Y"

start_date = datetime.datetime.strptime(sd, DATE_FORMATTER)
end_date = datetime.datetime.strptime(ed, DATE_FORMATTER)

def url_generator(start_date, end_date):
    current_date = start_date
    urls = []
    for day in range((end_date - start_date).days):
        urls.append(URL + current_date.strftime(DATE_FORMATTER))
        current_date += datetime.timedelta(days=1)
    return urls

urls = url_generator(start_date, end_date)



def parse_page(title, url, date):
    print("GOT {} - {}".format(title, url))
    # print(url)
    page = requests.get(url)
    response = html.fromstring(page.content) 
    # assert url == response.url

    body_text = " ".join(text.strip() for text in response.xpath(SELECTORS.GRAB_NEWS_BODY))
    reporter = response.xpath(SELECTORS.GRAB_REPORTER)
    breadcrumb = response.xpath(SELECTORS.GRAB_BREADCRUMB)
    
    data = dict(
        permalink=url,
        date=date,
        title=title,
        reporter=reporter,
        breadcrumb=breadcrumb,
        news=body_text
    )

    news.update_one({ 'permalink' : url }, {"$set" : data } , upsert=True)


async def fetch_page(url):
    _date = url.split('=')[-1]
    print("PARSING {}".format(_date))
    page = requests.get(url).content
    tree = html.fromstring(page)

    titles = tree.xpath("//h5/a//text()")
    links = [BASE_URL + x for x in  tree.xpath("//h5/a//@href") ]

    for link, title in zip(links, titles):
        _title = title.lower().translate(punct_remover)

        if any([keyword in _title for keyword in FILTER_KEYWORDS]):
            # print(link, title)
            # news.update_one({'permalink' : BASE_URL + link}, { '$set' : {'permalink' : BASE_URL + link }}, upsert=True)
            parse_page(title, link, _date)
            # print(link, title)

async def main():
    tasks = [asyncio.ensure_future(fetch_page(url)) for url in urls]
    await asyncio.wait(tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(main()))