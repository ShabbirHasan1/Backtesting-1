# Creating Hanging Man indicator

# input: Price_data: Date, Open, High, Low, Close, Volume

# Output: Hanging Man
import numpy as np


def hanging_man(price_data):

    Open = price_data["Open"]
    High = price_data["High"]
    Low = price_data["Low"]
    Close = price_data["Close"]

    price_data["Indicator"] = np.where(((np.minimum(Open, Close) - Low) > 2 * abs(Open - Close)) &
                                       ((High - np.maximum(Open, Close)) < 0.2 * (High - Low)) &
                                       (abs(Open - Close) < 0.2 * (High - Low)),
                                       1, 0)

    return price_data["Indicator"]
