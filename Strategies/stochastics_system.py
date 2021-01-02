from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

import numpy as np


def stochastics_system(price_data, period1=14,period2=3,long_level=50,short_level=50, long_stop=0,short_stop=0, period="", trade_type="Both_leg", underlying_instrument_data=None):

    if long_stop==0:
        long_stop=short_level
    if short_stop==0:
        short_stop=long_level

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    highest_high=price_period["High"].rolling(period1).max()
    lowest_low=price_period["Low"].rolling(period1).min()

    percentage_k=((price_period["Close"]-lowest_low)/(highest_high-lowest_low))*100

    price_signal_period = price_period

    price_signal_period["percentage_d"] = percentage_k.rolling(period2).mean()


    price_signal = price_data

    price_signal_period["Signal"] = np.where(((price_signal_period["percentage_d"] > long_level) & (price_signal_period["percentage_d"].shift() < long_level)), 1,
                                             np.where(((price_signal_period["percentage_d"] < short_level) & (price_signal_period["percentage_d"].shift() > short_level)), -1,
                                             np.where(((price_signal_period["percentage_d"] < long_stop) & (price_signal_period["percentage_d"].shift() > long_stop)),0,
                                                      np.where(((price_signal_period["percentage_d"] > short_stop) & (price_signal_period["percentage_d"].shift() < short_stop)),0,
                                                               np.nan))))
    price_signal_period["Signal"].fillna(method="ffill",inplace=True)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal
