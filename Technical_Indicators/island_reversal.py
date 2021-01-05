# Creating Island Reversal indicator

# input: Price_data: Date, Open, High, Low, Close, Volume

# Output: Island Reversal Indicator
import numpy as np

def island_reversal(price_data):

    price_data["Indicator"] = np.where((price_data["Low"]>price_data["High"].shift()) &
                                       (price_data["Low"].shift(2)>price_data["High"].shift()),1,
                                       np.where((price_data["High"]<price_data["Low"].shift()) &
                                       (price_data["High"].shift(2)<price_data["Low"].shift()),-1,0))


    return price_data["Indicator"]