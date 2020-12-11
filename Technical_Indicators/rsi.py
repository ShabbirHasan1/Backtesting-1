# Creating RSI indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: RSI indicator
import pandas as pd

def rsi(price_data, period):

    price_change = price_data["Close"].diff()
    up_days = price_change.where(price_change > 0, 0)
    down_days = price_change.where(price_change < 0, 0)
    down_days = down_days.abs()

    up_days_average = up_days.rolling(period).mean()
    down_days_average = down_days.rolling(period).mean()

    RS = up_days_average/down_days_average

    RSI = 100-(100/(1+RS))
    RSI.fillna(0, inplace=True)

    price_data["rsi"]=RSI


    return RSI
