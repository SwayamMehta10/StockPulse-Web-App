from flask import Flask, render_template, request, jsonify
import pandas as pd
import yfinance as yf
import plotly.express as px
from indicators import add_trace
from sentiment import sentiment_scores
from plot_risk import plot_risk_scores
from get_ticks_news import *
import google.generativeai as genai
from os import getenv
from PIL import Image
from prophet import Prophet
from prophet.plot import plot_plotly

# from sklearn.metrics import mean_absolute_error
# import requests
# from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

# from urllib.request import urlopen, Request
# from urllib.error import HTTPError

GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro-vision")

app = Flask(__name__)


df = pd.read_csv("static/data/NSE_EQUITY_L.csv")
companySymbols = df["SYMBOL"].tolist()
companyNames = df["NAME OF COMPANY"].tolist()
numberOfCompanies = df.shape[0]
options = []
for i in range(numberOfCompanies):
    options.append(companyNames[i] + " : " + companySymbols[i])


@app.route("/api/key")
def get_api_key():
    return jsonify({"api_key": GOOGLE_API_KEY})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about-us")
def aboutUs():
    return render_template("aboutUs.html")


@app.route("/company-background")
def companyBackground():
    return render_template("companyBackground.html", companyNames=options)


def format_value(value):
    if isinstance(value, pd.Series):
        return value.apply(format_value)
    elif pd.isna(value) or value == 0.0:
        return "---"
    elif abs(value) >= 1e7:
        return f"₹{value / 1e7:.2f} Cr."
    elif abs(value) >= 1e5:
        return f"₹{value / 1e5:.2f} Lakh"
    else:
        return f"₹{value / 1e3:.2f} K"


@app.route("/get-financial-statement", methods=["POST"])
def get_financial_statement():
    ticker = request.json["ticker"]
    statement_type = request.json["statement_type"]
    # print(statement_type)
    company = yf.Ticker(ticker)
    if statement_type == "income":
        financial_statement = company.incomestmt
    elif statement_type == "quarterly_income":
        financial_statement = company.quarterly_incomestmt
    elif statement_type == "cashflow":
        financial_statement = company.cashflow
    elif statement_type == "balancesheet":
        financial_statement = company.balancesheet
    else:
        financial_statement = company.quarterly_balancesheet

    financial_statement.columns = financial_statement.columns.strftime("%Y-%m-%d")

    financial_statement = financial_statement.apply(format_value)
    financial_statement = financial_statement.to_html()
    return financial_statement


@app.route("/get-company-info", methods=["POST"])
def getCompanyInfo():
    ticker = request.json["ticker"]
    company = yf.Ticker(ticker)
    website = company.info["website"]
    summary = company.info["longBusinessSummary"]
    sector = company.info["sector"]
    industry = company.info["industry"]
    risk_plot = plot_risk_scores(company.info)
    return jsonify(
        summary=summary,
        website=website,
        sector=sector,
        industry=industry,
        risk_plot=risk_plot,
    )


def format_year(value):
    if pd.isna(value):
        return "---"
    else:
        return int(value)


@app.route("/get-key-executives", methods=["POST"])
def getKeyExecutives():
    ticker = request.json["ticker"]
    company = yf.Ticker(ticker)
    df = pd.DataFrame(company.info["companyOfficers"])
    required_columns = ["name", "title", "yearBorn", "totalPay"]

    existing_columns = [col for col in required_columns if col in df.columns]
    if not existing_columns:
        return "Data Not Available"

    df = df[existing_columns]

    if "totalPay" in df.columns:
        df["totalPay"] = df["totalPay"].apply(format_value)
        df.rename(columns={"totalPay": "Pay"}, inplace=True)
    if "yearBorn" in df.columns:
        df["yearBorn"] = df["yearBorn"].apply(format_year)
        df.rename(columns={"yearBorn": "Year Born"}, inplace=True)
    df.rename(
        columns={
            "name": "Name",
            "title": "Title",
        },
        inplace=True,
    )
    df = df.to_html(index=False)
    return df


@app.route("/forecast")
def forecast():
    return render_template("forecast.html", companyNames=options)


@app.route("/forecast-price", methods=["POST"])
def forecastPrice():
    company = request.json["company"].split(":")
    ticker = company[1].strip()
    # companyOfficialName = company[0].strip()
    # Debugging
    # print(ticker)
    # print(companyOfficialName)
    period = request.json["period"]
    df = yf.download(ticker, period="5y")
    if df.empty:
        df = yf.download(ticker)
    df = df.reset_index()

    data = df[["Date", "Adj Close"]]
    data.rename(columns={"Date": "ds", "Adj Close": "y"}, inplace=True)
    model = Prophet()
    model.fit(data)
    if "W" in period:
        period = int(period[0]) * 7
    elif "M" in period:
        period = int(period[0]) * 30
    elif "Y" in period:
        period = int(period[0]) * 365
    future = model.make_future_dataframe(periods=period)
    forecast = model.predict(future)
    fig1 = plot_plotly(model, forecast)
    fig1.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    plot_html = fig1.to_html(full_html=False, default_height=500, default_width=700)
    return jsonify(plot=plot_html)


@app.route("/news-feed", methods=["POST"])
def newsFeed():
    words = request.json["company"].split()
    limited = words[:-1]
    company_without_limited = " ".join(limited)
    tickertape = pd.read_csv("static/data/tickertape.csv")
    similarities = [
        (name, fuzz.partial_ratio(company_without_limited.lower(), name.lower()))
        for name in tickertape["stock"]
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar = similarities[0]
    ticker = tickertape[tickertape["stock"] == most_similar[0]]["tick"]
    ticker = str(ticker.iloc[0])
    news_df = get_news(ticker)
    fig, sentiment_score = sentiment_scores(news_df[["Headline"]])
    headlines = news_df["Headline"].to_list()
    timestamps = news_df["Timestamp"].to_list()
    sources = news_df["Source"].to_list()
    links = news_df["Link"].to_list()
    fig = fig.to_html(full_html=False, default_height=500, default_width=500)
    return jsonify(
        headlines=headlines,
        timestamps=timestamps,
        sources=sources,
        links=links,
        plot=fig,
        score=sentiment_score,
    )


@app.route("/technical-analysis")
def technicalAnalysis():
    return render_template("technicalAnalysis.html", companyNames=options)


@app.route("/fetch-stock-data", methods=["POST"])
def fetch_stock_data():
    company = request.json["company"].split(":")
    ticker = company[1].strip()
    companyOfficialName = company[0].strip()
    indicator = request.json["indicator"]
    period = request.json["period"]
    start_date = request.json["startDate"]
    end_date = request.json["endDate"]

    # Debugging
    # print(ticker)
    # print(companyOfficialName)
    # print(indicator)
    # print(period)
    # print(start_date)
    # print(end_date)

    if start_date and end_date:
        data = yf.download(ticker, start=start_date, end=end_date)
    else:
        if period == "1d":
            data = yf.download(ticker, period=period, interval="1m")
        elif period == "5d":
            data = yf.download(ticker, period=period, interval="15m")
        else:
            data = yf.download(ticker, period=period)

    data = data.round(2)
    # print(data.head())

    fig = px.line(data, x=data.index, y="Close", hover_data=data.columns)
    fig.update_layout(
        title_text=companyOfficialName + " Price Chart",
        width=1500,
        hovermode="x unified",
    )
    fig.update_xaxes(rangeslider_visible=True)

    add_trace(fig, data, indicator)
    print("Figure created")
    fig.write_image("plot.png")
    print("Saved")
    plot_html = fig.to_html(full_html=False, default_height=500, default_width=700)

    # Open the PNG file
    image = Image.open("plot.png")
    response = model.generate_content(
        [
            "Give the theoretical underpinnings of every technical indicator (if presented) in the image. Identify trends in the stock price and the potential significance of the technical indicators with specific values. Discuss the overall sentiment and potential investibility of the stock based on the information presented in the graph. Include specific values only when you are sure about the datapoint in the image. Suggest other important information that user should research upon. Don't repeat any information and only refer to investors as 'you'.",
            image,
        ]
    )
    # print(response.text)

    return jsonify(plot=plot_html, explanation=response.text)


@app.route("/fetch-stock-price", methods=["POST"])
def fetch_stock_price():
    try:
        if request.is_json:
            request_data = request.get_json()
            if "tickerSymbol" in request_data:
                ticker_symbol = request.json["tickerSymbol"]
                company_official_name = request.json["companyOfficialName"].title()
                stock_history = yf.download(ticker_symbol, period="1d")
                # print(stock_history['Close'].iloc[0])
                return jsonify(
                    {
                        "text": f"The last closing price of {company_official_name} is ₹{round(stock_history['Close'].iloc[0], 2)}"
                    }
                )
            else:
                return (
                    jsonify({"text": "Ticker symbol not provided in the request."}),
                    400,
                )
        else:
            return jsonify({"text": "Request content type is not JSON."}), 415
    except Exception as e:
        return jsonify({"text": f"Error: {str(e)}"}), 500


@app.route("/fetch-official-company-name", methods=["POST"])
def fetch_official_company_name():
    try:
        if request.is_json:
            request_data = request.get_json()
            if "companyName" in request_data:
                global companyNames
                global companySymbols
                company_name = request.json["companyName"]

                # Calculate similarity between company_name and each company name
                similarities = [
                    (name, fuzz.partial_ratio(company_name.lower(), name.lower()))
                    for name in companyNames
                ]

                # Sort by similarity (highest to lowest)
                similarities.sort(key=lambda x: x[1], reverse=True)

                # Get the most similar company name
                most_similar = similarities[0]

                return jsonify({"text": most_similar[0]})
            else:
                return (
                    jsonify({"text": "Company Name not provided in the request."}),
                    400,
                )
        else:
            return jsonify({"text": "Request content type is not JSON."}), 415
    except Exception as e:
        return jsonify({"text": f"Error: {str(e)}"}), 500
