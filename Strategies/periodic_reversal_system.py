from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd

def periodic_reversal_system(price_data, period_1=14,period="",trade_type="Both_leg", underlying_instrument_data=None):

    if period=="":
        price_period=price_data
    else:
        price_period=series_resampling.price_series_periodic(price_data,period)


    price_signal = price_data
    price_signal_period = price_period

    price_signal_period["Signal"]=signal_generation(price_signal_period.index,period_1)


    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)


    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal

def signal_generation(dates,period):
    signal=pd.Series(index=dates)
    trade_position=1
    for i in range(1,len(dates),period):
        if trade_position==-1:
            signal[i]=1
            trade_position=1
        else:
            signal[i]=-1
            trade_position=-1
    signal.fillna(method="ffill",inplace=True)

    return signal