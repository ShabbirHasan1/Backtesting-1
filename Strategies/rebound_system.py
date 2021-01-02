from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd

def rebound_system(price_data, period="", trade_type="Both_leg",
                    underlying_instrument_data=None):
    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["Signal"]=0

    signal_generation(price_signal_period)
    price_signal_period["Signal"]=price_signal_period["Signal"].shift()

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal

def signal_generation(price_signal_period):
    previous_signal=0

    for i in range(2,len(price_signal_period.index)):

        High=price_signal_period["High"].iloc[i]
        Low=price_signal_period["Low"].iloc[i]

        high_1_days_back=price_signal_period["High"].iloc[i-1]
        low_1_days_back = price_signal_period["Low"].iloc[i - 1]

        high_2_days_back = price_signal_period["High"].iloc[i - 2]
        low_2_days_back = price_signal_period["Low"].iloc[i - 2]

        if previous_signal==1:
            if (High<high_1_days_back) & (high_2_days_back < high_1_days_back):
                signal=-1
                previous_signal=signal
            else:
                signal=previous_signal
        elif previous_signal==-1:
            if (Low > low_1_days_back) & (low_2_days_back > low_1_days_back):
                signal=1
                previous_signal=signal
            else:
                signal=previous_signal
        else:
            if (Low<low_1_days_back) & (low_2_days_back < low_1_days_back):
                signal=1
                previous_signal=signal
            elif (High>high_1_days_back) & (high_2_days_back > high_1_days_back):
                signal=-1
                previous_signal=signal
            else:
                signal=previous_signal
        price_signal_period["Signal"].iloc[i]=signal

    return price_signal_period["Signal"]