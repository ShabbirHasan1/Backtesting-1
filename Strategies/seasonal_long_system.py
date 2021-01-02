import numpy as np
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

def seasonal_long_system(price_data,entry_date=24,exit_date=4,period="", trade_type="Both_leg", underlying_instrument_data=None):

    period=""

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["Signal"]=1



    if entry_date<exit_date:
        price_signal_period["Signal"][price_signal_period.index.day > exit_date] = 0
        price_signal_period["Signal"][ price_signal_period.index.day <= entry_date] = 0
    else:
        price_signal_period["Signal"][price_signal_period.index.day > exit_date] = 0
        price_signal_period["Signal"][price_signal_period.index.day > entry_date] = 1

    price_signal_period.loc[price_signal_period["Signal"].shift(-1)==1,"Signal"] = 1

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"] = price_signal["Signal"].shift(1)
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)
    price_signal["Trades"].fillna(0, inplace=True)



    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal, "Close")

    return trades, price_signal
