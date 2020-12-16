# Creating Bollinger band percentage indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: SMA series

def bollinger_percentage(price_data, period):
    period_sma = str(period) + "_SMA"
    price_data[period_sma] = price_data["Close"].rolling(period).mean()
    price_data[period_sma].fillna(value=0, inplace=True)
    price_data["Bollinger percentage"]=(price_data["Close"]-price_data[period_sma])/price_data["Close"].rolling(period).std(ddof=0)

    return price_data["Bollinger percentage"]