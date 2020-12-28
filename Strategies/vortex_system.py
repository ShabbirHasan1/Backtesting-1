from Technical_Indicators import vortex as vortex
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import pandas as pd
import numpy as np


def vortex_system(price_data, period="", trade_type="Both_leg", underlying_instrument_data=None):

    if period=="":
        price_period=price_data
    else:
        price_period=series_resampling.price_series_periodic(price_data,period)

    price_signal = price_data
    price_signal_period = price_period

    vortex.vortex(price_period)

    price_signal_period["Signal"] = np.where((price_signal_period["Vortex"]>0), 1, -1)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"] = price_signal["Signal"].shift(1)
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)
    price_signal["Trades"].fillna(0,inplace=True)


    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Open"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal, "Open")

    return trades,price_signal
