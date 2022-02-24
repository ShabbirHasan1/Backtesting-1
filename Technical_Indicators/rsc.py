# Creating RSC indicator

# input: Price_data: Date, Open, High, Low, Close, Volume; Period
# Benchmark_Price_data: Date, Open, High, Low, Close, Volume; Period
# Period

# Output: RSI indicator

import pandas as pd

def rsc(price_data, benchmark_data,period=10):

    close_data=pd.DataFrame(columns=["Stock","Benchmark","Ratio","Ratio_ma"],index=price_data.index)
    close_data["Stock"]=price_data["Close"]
    close_data["Benchmark"]=benchmark_data["Close"]
    close_data["Ratio"]=close_data["Stock"]/close_data["Benchmark"]
    close_data["Ratio_ma"]=close_data["Ratio"].rolling(period).mean()
    rsc=close_data["Ratio"]/close_data["Ratio_ma"]


    return rsc
