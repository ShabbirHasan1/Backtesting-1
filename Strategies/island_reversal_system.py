from Technical_Indicators import island_reversal as island_reversal
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd

previous_signal = 0
profit_target_stop =0
stop_level_target =0


def island_reversal_system(price_data,profit_target=10,stop_level=2, period="", trade_type="Both_leg", underlying_instrument_data=None):
    profit_target=profit_target/100
    stop_level=-stop_level/100

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    island_reversal.island_reversal(price_signal_period)

    price_signal_period["Signal"] = price_signal_period.apply(lambda x: signal_generation(*x,profit_target,stop_level), axis=1 )

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal


def signal_generation(Open, High, Low, Close, Volume, indicator, profit_target, stop_level):
    global previous_signal
    global profit_target_stop
    global stop_level_target


    if indicator!=0:
        signal=indicator
        if signal==1:
            profit_target_stop = Close * (1 + profit_target)
            stop_level_target=Low*(1+stop_level)
        else:
            profit_target_stop = Close * (1 - profit_target)
            stop_level_target=High*(1-stop_level)
        previous_signal=signal
    elif previous_signal!=0:
        if previous_signal==1:
            if High>profit_target_stop or Low<stop_level_target:
                signal=0
                previous_signal=0
            else:
                signal=previous_signal
        else:
            if Low<profit_target_stop or High>stop_level_target:
                signal=0
                previous_signal=0
            else:
                signal=previous_signal
    else:
        signal=0
    return signal
