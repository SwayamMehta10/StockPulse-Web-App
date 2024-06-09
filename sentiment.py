import nltk
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import plotly.graph_objs as go


def sentiment_scores(news):
    analyzer = SentimentIntensityAnalyzer()
    scores = news["Headline"].apply(analyzer.polarity_scores).tolist()
    df_scores = pd.DataFrame(scores)
    news = news.join(df_scores, rsuffix="_right")
    news.rename(
        columns={
            "neg": "Negative",
            "neu": "Neutral",
            "pos": "Positive",
            "compound": "Sentiment Score",
        },
        inplace=True,
    )
    fig = plot_sentiment(news)
    sentiment_score = round(news['Sentiment Score'].mean(), 2)
    return fig, sentiment_score


def plot_sentiment(df):
    df["Total"] = df["Positive"] + df["Negative"] + df["Neutral"]
    df["Neutral"] = df["Neutral"] + (1 - df["Total"])
    aggregate_sentiment = df[["Positive", "Negative", "Neutral"]].sum()
    labels = ["Positive", "Negative", "Neutral"]
    values = aggregate_sentiment.values
    # print(values)
    colors = ["green", "red", "blue"]
    pie_chart = go.Pie(labels=labels, values=values, marker=dict(colors=colors), hoverinfo='label+percent')
    layout = go.Layout(margin=dict(l=10, r=10, t=10, b=10))
    fig = go.Figure(data=[pie_chart], layout=layout)
    return fig
