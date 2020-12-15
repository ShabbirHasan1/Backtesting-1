from Technical_Indicators import sma as sma, rsi as rsi
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

import numpy as np

entry_level=0
previous_signal=0

def rsi2_50sma_system(price_data, period_sma, period_rsi, stop_level=100, period="", trade_type="Both_leg",
                      underlying_instrument_data=None):

    stop_level=stop_level/100

    period_sma_str = str(period_sma) + "_SMA"

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    sma.sma(price_period, period_sma)
    rsi.rsi(price_period, period_rsi)

    price_signal_period = price_period

    price_signal = price_data

    # price_signal_period[period_sma] = sma_1

    price_signal_period["Signal_sma"] = np.where((price_signal_period[period_sma_str] <= price_signal_period["Close"]),
                                                 1, -1)

    price_signal_period["rsi_1"] = price_signal_period["rsi"].shift(1)
    price_signal_period["rsi_1"].fillna(0,inplace=True)

    price_signal_period["Signal_rsi"] = np.where(((price_signal_period["rsi"] > 10) & (price_signal_period["rsi_1"] <10)),1, np.where(
        ((price_signal_period["rsi"] < 90) & (price_signal_period["rsi_1"] > 90)),-1,0))

    price_signal_period["Signal_rsi"].replace(to_replace=0,method="ffill",inplace=True)

    price_signal_period["Signal_1"] = np.where(
        ((price_signal_period["Signal_sma"] == price_signal_period["Signal_rsi"]) & (price_signal_period["Signal_rsi"]== 1)), 1,
        np.where(((price_signal_period["Signal_sma"] == price_signal_period["Signal_rsi"]) & (price_signal_period["Signal_rsi"]== -1)), -1, 0))

    price_signal["Signal_1"] = price_signal_period["Signal_1"].resample("D").ffill()
    price_signal["Signal_1"].fillna(0, inplace=True)

    price_signal["Signal"] = price_signal[["Close","Signal_1"]].apply(
        lambda x: stop_loss(*x,stop_level), axis=1)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal

def stop_loss(close,signal_1,stop_level):

    global entry_level
    global previous_signal

    if signal_1 != previous_signal:
        entry_level = close
        signal=signal_1
        previous_signal = signal_1

    elif previous_signal == 1:
        if close/entry_level < (1-stop_level):
            signal=0
        else:
            signal=signal_1

    elif previous_signal == -1:
        if close/entry_level > (1+stop_level ):
            signal=0
        else:
            signal=signal_1

    else:
        signal=signal_1

    previous_signal=signal_1

    return signal