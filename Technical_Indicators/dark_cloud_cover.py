# Creating Dark cloud cover indicator

# input: Price_data: Date, Open, High, Low, Close, Volume

# Output: Dark Cloud cover
import numpy as np

def dark_cloud_cover(price_data):

    price_data["Indicator"] = np.where((price_data["Open"]>price_data["Close"]) &
                                       (price_data["Open"].shift() < price_data["Close"].shift()) &
                                       (price_data["Open"] > price_data["High"].shift()) &
                                       (price_data["Close"] > price_data["Low"].shift()) &
                                       (price_data["Close"]<(0.5*(price_data["High"].shift()-price_data["Low"].shift())+price_data["Low"].shift())),1,0)


    return price_data["Indicator"]