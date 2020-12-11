# Creating weighted moving average indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: WMA series

import numpy as np

def wma(price_data, period):
    period_wma = str(period) + "_wma"
    wma_range = np.array(range(1,period+1))

    price_data[period_wma] = price_data["Close"].rolling(window=period).apply(lambda x:((x*wma_range).sum())/(wma_range.sum()))
    price_data[period_wma].fillna(value=0, inplace=True)
    return price_data[period_wma]
