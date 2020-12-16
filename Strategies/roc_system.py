from Technical_Indicators import roc as roc
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import pandas as pd
import numpy as np


def roc_system(price_data, period1=10, period2=25, period3=40, period="", trade_type="Both_leg", underlying_instrument_data=None):

    if period=="":
        price_period=price_data
    else:
        price_period=series_resampling.price_series_periodic(price_data,period)

    price_signal = price_data
    price_signal_period = price_period

    roc.roc(price_period, period1)
    roc.roc(price_period, period2)
    roc.roc(price_period, period3)

    price_signal_period["roc_average"] = price_period[[str(period1)+"_roc",str(period2)+"_roc",str(period3)+"_roc"]].mean(axis=1)


    price_signal_period["Signal"] = np.where((price_signal_period["roc_average"]>0), 1, -1)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)
    price_signal["Trades"].fillna(0,inplace=True)


    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal,None,underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades,price_signal
