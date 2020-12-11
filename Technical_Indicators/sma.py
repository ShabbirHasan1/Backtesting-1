# Creating simple moving average indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: SMA series

def sma(price_data, period):
    period_sma = str(period) + "_SMA"
    price_data[period_sma] = price_data["Close"].rolling(period).mean()
    price_data[period_sma].fillna(value=0, inplace=True)

    return price_data[period_sma]
