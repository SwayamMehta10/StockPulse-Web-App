import pandas as pd
import numpy as np
import plotly.graph_objects as go


# Compute the Bollinger Bands
# 50-day ma
def BBANDS(data, window=50):
    MA = data.Close.rolling(window).mean()
    SD = data.Close.rolling(window).std()
    data["MiddleBand"] = MA
    data["UpperBand"] = MA + (2 * SD)
    data["LowerBand"] = MA - (2 * SD)
    return data


# 50-day Simple Moving Average
def SMA(data, ndays=50):
    SMA = pd.Series(data["Close"].rolling(ndays).mean(), name="SMA")
    data = data.join(SMA)
    data.dropna(inplace=True)
    return data


# 200-day Exponentially-weighted Moving Average
def EWMA(data, ndays=200):
    EMA = pd.Series(
        data["Close"].ewm(span=ndays, min_periods=ndays - 1).mean(),
        name="EWMA_" + str(ndays),
    )
    data = data.join(EMA)
    data.dropna(inplace=True)
    return data


# RSI
def rsi(close, periods=14):

    close_delta = close.diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi


# Calculate money flow index
def mfi(high, low, close, volume, n=14):
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    mf_sign = np.where(typical_price > typical_price.shift(1), 1, -1)
    signed_mf = money_flow * mf_sign

    # Calculate gain and loss using vectorized operations
    positive_mf = np.where(signed_mf > 0, signed_mf, 0)
    negative_mf = np.where(signed_mf < 0, -signed_mf, 0)

    mf_avg_gain = pd.Series(positive_mf).rolling(n, min_periods=1).sum()
    mf_avg_loss = pd.Series(negative_mf).rolling(n, min_periods=1).sum()

    return (100 - 100 / (1 + mf_avg_gain / mf_avg_loss)).to_numpy()


# Returns ATR values
def atr(high, low, close, n=14):
    tr = np.amax(
        np.vstack(
            (
                (high - low).to_numpy(),
                (abs(high - close)).to_numpy(),
                (abs(low - close)).to_numpy(),
            )
        ).T,
        axis=1,
    )
    return pd.Series(tr).rolling(n).mean().to_numpy()


# # Returns the Force Index
# def ForceIndex(data, ndays=1):
#     FI = pd.Series(data["Close"].diff(ndays) * data["Volume"], name="ForceIndex")
#     data = data.join(FI)
#     return data


# 14-day Ease of Movement
def EMV(data, ndays=14):
    dm = ((data["High"] + data["Low"]) / 2) - (
        (data["High"].shift(1) + data["Low"].shift(1)) / 2
    )
    br = (data["Volume"] / 100000000) / ((data["High"] - data["Low"]))
    EMV = dm / br
    EMV_MA = pd.Series(EMV.rolling(ndays).mean(), name="EMV")
    data = data.join(EMV_MA)
    return data


def add_trace(fig, data, indicator):
    if "sma" in indicator:
        data = SMA(data)
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["SMA"],
                mode="lines",
                name="50-day SMA",
                line=dict(color="yellow"),
            )
        )

    if "ewma" in indicator:
        data = EWMA(data)
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EWMA_200"],
                mode="lines",
                name="200-day EWMA",
                line=dict(color="orange"),
            )
        )

    if "bb" in indicator:
        data = BBANDS(data)
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["UpperBand"],
                mode="lines",
                name="Upper Band",
                line=dict(color="green"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MiddleBand"],
                mode="lines",
                name="Middle Band",
                line=dict(color="red"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["LowerBand"],
                mode="lines",
                name="Lower Band",
                line=dict(color="green"),
            )
        )

    if "rsi" in indicator:
        data["RSI"] = rsi(data["Close"])
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["RSI"],
                mode="lines",
                name="RSI",
                line=dict(color="purple"),
            )
        )

    if "mfi" in indicator:
        data["MFI"] = mfi(data["High"], data["Low"], data["Close"], data["Volume"])
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["MFI"],
                mode="lines",
                name="Money Flow Index",
                line=dict(color="cyan"),
            )
        )

    if "atr" in indicator:
        data["ATR"] = atr(data["High"], data["Low"], data["Close"])
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["ATR"],
                mode="lines",
                name="Average True Range",
                line=dict(color="grey"),
            )
        )

    # if 'fi' in indicator:
    #     data = ForceIndex(data)

    if "emv" in indicator:
        data = EMV(data)
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMV"],
                mode="lines",
                name="14-day Ease of Movement",
                line=dict(color="violet"),
            )
        )
