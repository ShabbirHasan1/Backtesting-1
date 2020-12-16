from Technical_Indicators import sma as sma
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd

previous_signal = 0
trade_level=0
trade_day_count=0


def series3_system(price_data, period="", trade_type="Both_leg", underlying_instrument_data=None):
    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    sma_100=sma.sma(price_signal_period,100)

    price_signal_period["sma_100_signal"]=np.where(price_signal_period["Close"]>sma_100,1,-1)

    price_signal_period["pattern_signal"]=np.where(((price_signal_period["Close"]>price_signal_period["Close"].shift(1))
                             & (price_signal_period["Close"].shift(1)>price_signal_period["Close"].shift(2))
                             & (price_signal_period["Close"].shift(2)>price_signal_period["Close"].shift(3))
                             & (price_signal_period["High"]>price_signal_period["High"].shift(1))
                             & (price_signal_period["High"].shift(1)>price_signal_period["High"].shift(2))
                             & (price_signal_period["High"].shift(2)>price_signal_period["High"].shift(3))
                             & (price_signal_period["Low"]>price_signal_period["Low"].shift(1))
                             & (price_signal_period["Low"].shift(1)>price_signal_period["Low"].shift(2))
                             & (price_signal_period["Low"].shift(2)>price_signal_period["Low"].shift(3)))
                            |((price_signal_period["Close"]<price_signal_period["Close"].shift(1))
                             & (price_signal_period["Close"].shift(1)<price_signal_period["Close"].shift(2))
                             & (price_signal_period["Close"].shift(2)<price_signal_period["Close"].shift(3))
                             & (price_signal_period["High"]<price_signal_period["High"].shift(1))
                             & (price_signal_period["High"].shift(1)<price_signal_period["High"].shift(2))
                             & (price_signal_period["High"].shift(2)<price_signal_period["High"].shift(3))
                             & (price_signal_period["Low"]<price_signal_period["Low"].shift(1))
                             & (price_signal_period["Low"].shift(1)<price_signal_period["Low"].shift(2))
                             & (price_signal_period["Low"].shift(2)<price_signal_period["Low"].shift(3)))
                             ,1,0)


    price_signal_period["Signal"] = price_signal_period.apply(lambda x: signal_generation(*x), axis=1)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal


def signal_generation(Open, High, Low, Close, Volume, sma_100, sma_100_signal, pattern_signal):
    global previous_signal
    global trade_day_count
    global trade_level

    if previous_signal==0:
        if pattern_signal==1:
            signal=sma_100_signal
            previous_signal=sma_100_signal
            trade_level=Close
            trade_day_count=0
        else:
            signal=0
    else:
        trade_day_count+=1
        trade_profit=((Close/trade_level)-1)*previous_signal
        if trade_day_count==16 or trade_profit > 0.10 or trade_profit < -0.03 :
            signal=0
            trade_day_count=0
            previous_signal=0
            trade_level=0
        else:
            signal=previous_signal

    return signal
