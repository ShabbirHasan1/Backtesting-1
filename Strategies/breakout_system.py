from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd

previous_signal = 0


def breakout_system(price_data, atr_period=44, daily_range_period=4, period="", trade_type="Both_leg",
                    underlying_instrument_data=None):
    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["Buy Level"] = price_signal_period["Open"] + (
                price_signal_period["CLose"].shift(1) - price_signal_period["Low"].shift(1))
    price_signal_period["Sell Level"] = price_signal_period["Open"] - (
                price_signal_period["High"].shift(1) - price_signal_period["Close"].shift(1))

    price_signal_period["Position window today"] = np.where(
        price_signal_period["Open"] >= price_signal_period["Close"].shift(1), 1, -1)

    price_signal_period["Position window yesterday"] = price_signal_period["Position window"].shift(1)

    Signal = price_signal_period.apply(lambda x: signal_generation(*x), axis=1)

    Signal = Signal.apply(pd.Series)
    Signal.columns = ["Signal", "Trade_Level"]
    price_signal_period = pd.concat([price_signal_period, Signal], axis=1)

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


def signal_generation(Open, High, Low, Close, Volume, Buy_level, Sell_level, Position_window_today, Position_window_yesterday):
    global previous_signal

    if previous_signal == 0:
        if Position_window_yesterday==1:
            if High > Buy_level:
                signal=1
                trade_level=Buy_level
                previous_signal=signal
            else:
                signal = 0
                trade_level = 0
        else:
            if Low < Sell_level:
                signal = -1
                trade_level = Sell_level
                previous_signal = signal
            else:
                signal = 0
                trade_level = 0

    elif previous_signal == 1:
        if Position_window_today==-1:
            if Low < Sell_level:
                if Position_window_yesterday==-1:
                    signal=-1
                    trade_level=Sell_level
                    previous_signal=signal
                else:
                    signal = 0
                    trade_level = Sell_level
                    previous_signal = signal
            else:
                signal = previous_signal
                trade_level = 0
        else:
            signal = previous_signal
            trade_level = 0
    else:
        if Position_window_today==1:
            if High > Buy_level:
                if Position_window_yesterday==1:
                    signal=1
                    trade_level=Buy_level
                    previous_signal=signal
                else:
                    signal = 0
                    trade_level = Buy_level
                    previous_signal = signal
            else:
                signal = previous_signal
                trade_level = 0
        else:
            signal = previous_signal
            trade_level = 0

    return signal, trade_level
