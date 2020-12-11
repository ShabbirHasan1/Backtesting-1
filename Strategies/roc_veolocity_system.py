from Technical_Indicators import roc as roc
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_close as tc
from Trade_Generation import creating_individual_trade
import numpy as np

previous_signal = 0


def roc_veolocity_system(price_data, period1=10, period2=25, period3=40, period="", trade_type="Both_leg", underlying_instrument_data=None):

    period1_str=str(period1)+"_roc"
    period2_str = str(period2) + "_roc"
    period3_str = str(period3) + "_roc"

    if period=="":
        price_period=price_data
    else:
        price_period=series_resampling.price_series_periodic(price_data,period)

    roc.roc(price_period, period1)
    roc.roc(price_period, period2)
    roc.roc(price_period, period3)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period[period1_str] = price_signal_period[period1_str] / period1
    price_signal_period[period2_str] = price_signal_period[period2_str] / period2
    price_signal_period[period3_str] = price_signal_period[period3_str] / period3
    price_signal_period["roc_average"] = price_signal_period[[period1_str, period2_str, period3_str]].mean(axis=1)

    price_signal_period["roc_indicator"] = price_signal_period[[period1_str, period2_str, period3_str]].apply(lambda x: indicator_generation(*x),
                                                                                    axis=1)

    price_signal_period["Signal"] = price_signal_period[["roc_indicator", "roc_average", period1_str]].apply(
        lambda x: signal_generation(*x), axis=1)
    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)


    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_close(price_signal)

    return trades,price_signal


def indicator_generation(roc_1, roc_2, roc_3):
    if roc_1 > roc_2 > roc_3 and roc_1 > 0:
        indicator = 1
    elif roc_1 < roc_2 < roc_3 and roc_1 < 0:
        indicator = -1
    else:
        indicator = 0

    return indicator


def signal_generation(roc_indicator, roc_average, roc_1):
    global previous_signal

    if roc_indicator != 0:
        signal = roc_indicator
    elif (roc_1 > roc_average and previous_signal == -1) or (roc_1 < roc_average and previous_signal == 1):
        signal = 0
    else:
        signal = previous_signal

    previous_signal = signal

    return signal
