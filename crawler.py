from lxml import etree
import requests
import datetime
from pymongo import MongoClient
from string import punctuation

punct_remover = str.maketrans('', '', punctuation )

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

import asyncio

async def fetch_page(url):
    url = requests.get(url)
    print(url.url)

async def main():
    tasks = [asyncio.ensure_future(fetch_page(url)) for url in urls]
    await asyncio.wait(tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(main()))