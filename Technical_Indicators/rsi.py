# Creating RSI indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: RSI indicator
import pandas as pd

def rsi(price_data, period: int):

    price_change = price_data["Close"].diff()
    up_days = price_change.where(price_change > 0, 0)
    down_days = price_change.where(price_change < 0, 0)
    down_days = down_days.abs()

    up_days_average = rolling_mean(up_days,period)
    down_days_average = rolling_mean(down_days,period)

    RS = up_days_average/down_days_average

    RSI = 100-(100/(1+RS))
    RSI.fillna(0, inplace=True)

    price_data["rsi"]=RSI

    return RSI

def rolling_mean(data,period):

    data_average= pd.Series(0,index=data.index)

    data_average.iloc[period]=data.iloc[1:period].mean()

    for i in data.index[period:]:
        data_average.loc[i] = (data_average.shift(1).loc[i]*(period-1)+data.loc[i])/period

    return data_average

