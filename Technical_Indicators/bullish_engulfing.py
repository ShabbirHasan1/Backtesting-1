# Creating bullish engulfing indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period

# Output: bullish engulfing
import numpy as np

def bullish_engulfing(price_data):

    price_data["Indicator"] = np.where((price_data["Open"].shift()>price_data["Close"].shift()) &
                                       (price_data["Open"] < price_data["Close"]) &
                                       (price_data["Open"] < price_data["Close"].shift()) &
                                       (price_data["Open"].shift() < price_data["Close"]),1,0)


    return price_data["Indicator"]