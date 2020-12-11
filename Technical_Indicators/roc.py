# Creating ROC indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: ROC indicator

def roc(price_data, period):

    roc_period=str(period)+"_roc"

    price_data[roc_period] = price_data["Close"].pct_change(period).fillna(0)

    return roc
