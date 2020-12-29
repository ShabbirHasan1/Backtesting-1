from Technical_Indicators import atr as atr
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd

previous_signal=0


def keltner_system(price_data, period1=21, period2=21 ,period="", trade_type="Both_leg", underlying_instrument_data=None):
    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["Average_close"] = price_signal_period[["High","Low","Close"]].mean(axis=1)
    price_signal_period["Average_close_average"]=price_signal_period["Average_close"].rolling(period1).mean()

    true_range=pd.concat([price_signal_period["High"]-price_signal_period["Low"],
                   abs(price_signal_period["High"]-price_signal_period["Close"].shift()),
                   abs(price_signal_period["Low"]-price_signal_period["Close"].shift())],axis=1)

    true_range=true_range.max(axis=1)

    price_signal_period["atr"]=true_range.rolling(period2).mean()

    price_signal_period["upper_band"]=price_signal_period["Average_close_average"]+1.3*price_signal_period["atr"]
    price_signal_period["lower_band"]=price_signal_period["Average_close_average"]-1.3*price_signal_period["atr"]

    cols=["Average_close_average","upper_band","lower_band"]

    price_signal_period[cols]=price_signal_period[cols].shift(fill_value=0)

    price_signal_period["Average_close_signal"]=np.where(price_signal_period["Average_close_average"]>=price_signal_period["Average_close_average"].shift(),1,-1)

    Signal=price_signal_period.apply(lambda x: signal_generation(*x), axis=1)

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

def signal_generation(open,high,low,close,volume,average,average_of_average,atr,upper_band,lower_band,average_signal):
    global previous_signal

    if previous_signal == 0:
        if high>upper_band and average_signal==1:
                signal=1
                trade_level=max(upper_band,open)
        elif low<lower_band and average_signal==-1:
                signal=-1
                trade_level=min(lower_band,open)
        else:
                signal=0
                trade_level=0
    elif previous_signal==1:
        if low<average_of_average:
            signal=0
            trade_level=min(average_of_average,open)
        else:
            signal=previous_signal
            trade_level=0
    else:
        if high > average_of_average:
            signal = 0
            trade_level = max(average_of_average, open)
        else:
            signal = previous_signal
            trade_level = 0

    previous_signal = signal

    return (signal, trade_level)
