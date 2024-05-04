import pandas as pd
from fuzzywuzzy import fuzz

tickertape = pd.read_csv("static/data/tickertape.csv")
nse = pd.read_csv("static/data/NSE_EQUITY_L.csv")

company = "20 Microns"
similarities = [(name, fuzz.partial_ratio(company.lower(), name.lower())) for name in tickertape["stock"]]
similarities.sort(key=lambda x: x[1], reverse=True)
most_similar = similarities[0]

print(most_similar, tickertape[tickertape["stock"]==most_similar[0]]["tick"])