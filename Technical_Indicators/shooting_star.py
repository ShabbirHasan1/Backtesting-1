# Creating Shooting Star indicator

# input: Price_data: Date, Open, High, Low, Close, Volume

# Output: Shooting Star Indicator
import numpy as np


def shooting_star(price_data):

    Open = price_data["Open"]
    High = price_data["High"]
    Low = price_data["Low"]
    Close = price_data["Close"]

    price_data["Indicator"] = np.where((Open > Close) &
                                       ((High - Open) > 2 * (Open - Close)) &
                                       (( Close - Low) < 0.2 * (High - Low)),
                                       1, 0)

    return price_data["Indicator"]
