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
ed = "01-09-2008"
DATE_FORMATTER = "%d-%m-%Y"

start_date = datetime.datetime.strptime(sd, DATE_FORMATTER)
end_date = datetime.datetime.strptime(ed, DATE_FORMATTER)

current_date = start_date

for day in range((end_date - current_date).days):
    
    get_current_date_page = requests.get(URL + current_date.strftime(DATE_FORMATTER))

    print(get_current_date_page.url)

    current_date += datetime.timedelta(days=1)
