from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen, Request
from urllib.error import HTTPError


def get_ticks(url):
    req = Request(url=url, headers={"User-Agent": "Chrome"})
    response = urlopen(req)
    html = BeautifulSoup(response, "html.parser")
    ticks_table = html.find(class_="page")
    ticks = list()
    stocks = list()
    for name_box in ticks_table.find_all("a", href=True):
        stocks.append(name_box.text.strip())
        ticks.append(name_box["href"].split("-")[-1].strip())
    d = {"stock": stocks, "tick": ticks}
    df = pd.DataFrame(data=d)
    return df


def get_stock_data():
    tick_df = pd.DataFrame()
    for letter in range(ord("a"), ord("z") + 1):
        url = "https://www.tickertape.in/stocks?filter=" + chr(letter)
        tick = get_ticks(url)
        tick_df = pd.concat([tick_df, tick], ignore_index=True)
    # print(tick_df.info())
    url = "https://www.tickertape.in/stocks?filter=others"
    tick = get_ticks(url)
    tick_df = pd.concat([tick_df, tick], ignore_index=True)
    tick_df.to_csv("static/data/tickertape.csv", index=False)


def get_headlines(url):
    try:
        req = Request(url=url, headers={"User-Agent": "Chrome"})
        response = urlopen(req).read()
        html = BeautifulSoup(response, "html.parser")
        a = html.findAll("a", class_=["jsx-3440134818 news-card d-flex-col mb32", "jsx-3953764037 news-card d-flex-row"])
        p = html.findAll("p", class_="shave-root")[1:]
        span = html.findAll("span", class_=["jsx-3440134818", "jsx-3953764037"])
        links = []
        headlines = []
        timestamps = []
        sources = []
        for link in a:
            if "#overlay-video" in link.get("href"):
                url = url.replace("news", "overlay-video")
                links.append(url)
                # print(url)
            else:
                links.append(link.get("href"))
                # print(link.get("href"))
        for line in p:  
            headlines.append(line.text.strip())
        for x in span:
            if "ago" in x.text.strip():
                timestamps.append(x.text.strip())
            elif "•" in x.text.strip() or "Video" in x.text.strip() or x.text.strip() == "":
                continue
            else:
                sources.append(x.text.strip())
        print(sources)
        news = pd.DataFrame({"Headline": headlines, "Timestamp": timestamps, "Source": sources, "Link": links})
        return news
    except HTTPError as e:
        if e.code == 308:
            new_url = e.headers["Location"]
            return get_headlines(new_url)
        else:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None

def get_news(tick):
    url = "https://www.tickertape.in/stocks/" + tick + "#news"
    news = get_headlines(url)
    # print(news)
    return news