from get_ticks_news import *
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen, Request
from urllib.error import HTTPError


print(get_news("RELI"))