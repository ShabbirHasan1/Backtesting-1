from Technical_Indicators import sma as sma
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd


def signal_generation(price_signal_period,trailing_stop):

    day_data=price_signal_period.itertuples()
    previous_std_signal=0
    previous_stop=0

    for day in day_data:

        if day.Index==price_signal_period.index[0]:
            previous_day=day
        else:
            std_signal= -1 if day.std_level<=-1 else(1 if day.std_level>=1 else 0)
            if (std_signal!=previous_std_signal and std_signal!=0 and std_signal!=price_signal_period["Signal"][previous_day.Index]):
                price_signal_period["Signal"][day.Index]=std_signal
                previous_stop=day.Close
            elif price_signal_period["Signal"][previous_day.Index]==1:
                if day.Close<(1-trailing_stop)*previous_stop:
                    price_signal_period["Signal"][day.Index]=0
                else:
                    price_signal_period["Signal"][day.Index]=1
                    previous_stop=max(day.Close,previous_stop)
            elif price_signal_period["Signal"][previous_day.Index]==-1:
                if day.Close > (1 + trailing_stop) * previous_stop:
                    price_signal_period["Signal"][day.Index] = 0
                else:
                    price_signal_period["Signal"][day.Index] = -1
                    previous_stop = min(day.Close, previous_stop)
            else:
                price_signal_period["Signal"][day.Index]=0
            previous_std_signal=std_signal
            previous_day = day

def ma_trailing_stop_system(price_data, std_period=20, trailing_stop=3, period="", trade_type="Both_leg", underlying_instrument_data=None):
    trailing_stop=trailing_stop/100

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["std_level"]=(price_signal_period["Close"]-price_signal_period["Close"].rolling(std_period).mean())/price_signal_period["Close"].rolling(std_period).std()

    price_signal_period["Signal"] =0

    signal_generation(price_signal_period,trailing_stop)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal


