# Creating macd indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: macd series

def macd(price_data):
    price_data["macd"] = price_data["Close"].ewm(span=12,adjust=False).mean()-price_data["Close"].ewm(span=26,adjust=False).mean()
    price_data["macd_signal"] = price_data["macd"].ewm(span=9, adjust=False).mean()
    price_data["macd_diff"] = price_data["macd"]-price_data["macd_signal"]

    price_data["macd"].fillna(value=0,inplace=True)
    price_data["macd_signal"].fillna(value=0, inplace=True)
    price_data["macd_diff"].fillna(value=0, inplace=True)

    return price_data[["macd","macd_signal","macd_diff"]]
