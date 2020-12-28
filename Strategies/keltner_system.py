from Technical_Indicators import atr as atr
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd


def keltner_system(price_data, period1=21, period2=21 ,period="", trade_type="Both_leg", underlying_instrument_data=None):
    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["Average Close"] = price_signal_period[["High","Low","Close"]].mean(axis=1)
    price_signal_period["Average Close average"]=price_signal_period["Average Close"].rolling(period1).mean()

    true_range=pd.concat([price_signal_period["High"]-price_signal_period["Low"],
                   abs(price_signal_period["High"]-price_signal_period["Close"].shift()),
                   abs(price_signal_period["Low"]-price_signal_period["Close"].shift())],axis=1)

    true_range=true_range.max(axis=1)

    atr=rolling_average(true_range,period2)

    signal_generation(price_signal_period)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trade_Level"] = price_signal_period["Trade_Level"]
    price_signal["Trade_Level"].fillna(0, inplace=True)


    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Trade_Level"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal, "Trade_Level")

    return trades, price_signal

def rolling_average(true_range,period2):
    for i in range(period2,len(true_range)):
        atr[i]=true_range.iloc[-period2-1:i]

def signal_generation(price_period_signal):

    for index, row in price_period_signal.iterrows():

        true_range=max(row)





    return (signal, trade_level)
