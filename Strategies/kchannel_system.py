from Technical_Indicators import atr as atr,ema as ema
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

import numpy as np


def kchannel_system(price_data, period1=20, period="", trade_type="Both_leg", underlying_instrument_data=None):
    period_ema = str(period1) + "_EMA"

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    ema.ema(price_period, period1)
    atr.atr(price_period,period1)

    price_period["Upper band"] = price_period[period_ema] + price_period["ATR"]
    price_period["Lower band"] = price_period[period_ema] - price_period["ATR"]

    price_signal_period = price_period

    price_signal = price_data

    price_signal_period["Signal"] = np.where((price_signal_period["Close"] > price_signal_period["Upper band"]), 1,
                                             np.where((price_signal_period["Close"] < price_signal_period["Lower band"]), -1,
                                             np.nan))
    price_signal_period["Signal"].fillna(method="ffill",inplace=True)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal
