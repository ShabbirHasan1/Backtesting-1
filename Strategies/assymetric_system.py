from Technical_Indicators import sma as sma
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_close as tc
from Trade_Generation import creating_individual_trade
import numpy as np


def assymetric_system(price_data, period_1, period_2, period="", trade_type="Both_leg", underlying_instrument_data=None):

    if period=="":
        price_period=price_data
    else:
        price_period=series_resampling.price_series_periodic(price_data,period)

    sma.sma(price_period,period_1)
    sma.sma(price_period, period_2)

    price_signal_period = price_period

    price_signal_period["min_of_2"]=price_signal_period[[str(period_1)+"_SMA",
                                                          str(period_2)+"_SMA"]].min(axis=1)

    price_signal = price_data

    price_signal_period["Signal"] = np.where((price_signal_period["Close"] > price_signal_period["min_of_2"]), 1,-1)

    price_signal["Signal"]=price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    price_signal.to_csv("Price_signal.csv", index=True)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_close(price_signal)

    return trades,price_signal
