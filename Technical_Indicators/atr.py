# Creating ATR indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: ATR series
import pandas as pd

def atr(price_data, period):
    high = price_data["High"]
    low = price_data["Low"]
    close = price_data["Close"]
    tr0 = abs(high - low)
    tr1 = abs(high - close.shift())
    tr2 = abs(low - close.shift())
    tr = pd.concat([tr0,tr1,tr2],axis=1)
    atr_1 = tr.max(axis=1)
    atr = atr_1.ewm(span=period,adjust=False).mean()

    price_data["ATR"]=atr

    return atr
