# Creating exponential moving average indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: EMA series

def ema(price_data, period):
    period_ema = str(period) + "_EMA"
    price_data[period_ema] = price_data["Close"].ewm(span=period,adjust=False).mean()
    price_data[period_ema].fillna(value=0, inplace=True)

    return price_data[period_ema]