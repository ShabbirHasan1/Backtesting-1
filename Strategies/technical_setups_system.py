from Technical_Indicators import bullish_engulfing as indicator1
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

import numpy as np

def bullish_engulfing_system(price_data, period1=20, period="",trade_type="Both_leg", underlying_instrument_data=None):

    if period=="":
        price_period=price_data
    else:
        price_period=series_resampling.price_series_periodic(price_data,period)


    indicator1.bullish_engulfing(price_period)

    price_signal_period = price_period

    price_signal = price_data

    price_signal_period["Signal"] = np.where(price_signal_period["Indicator"].rolling(period1).sum()>0,1,0)
    price_signal_period["Signal"]=price_signal_period["Signal"].shift()

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal
