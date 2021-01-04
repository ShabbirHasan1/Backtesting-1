from Technical_Indicators import ema as ema
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade
import numpy as np
import pandas as pd


def signal_generation(price_signal_period, profit_target, trailing_stop):
    day_data = price_signal_period.itertuples()

    trade_entry = 0
    trade_side = 0

    for day in day_data:
        if day.Close == 1351:
            print("Hey")

        if day.Index == price_signal_period.index[0]:
            previous_day = day
        else:
            if previous_day.Trade_signal == 0 and day.Trade_signal != 0 and day.Trade_signal!=trade_side:
                price_signal_period["Signal"][day.Index] = day.Trade_signal
                trade_side = day.Trade_signal
                trade_entry = day.Close
            elif trade_side != 0:
                current_profit = ((day.Close - trade_entry) / trade_entry) * trade_side
                if (current_profit > profit_target) or (current_profit < trailing_stop):
                    price_signal_period["Signal"][day.Index] = 0
                    trade_side=0
                elif trade_side == 1 and (day.High < previous_day.Upper_band):
                    price_signal_period["Signal"][day.Index] = 0
                    trade_side=0
                elif trade_side == -1 and (day.Low > previous_day.Lower_band):
                    price_signal_period["Signal"][day.Index] = 0
                    trade_side=0
                else:
                    price_signal_period["Signal"][day.Index] = trade_side
            else:
                price_signal_period["Signal"][day.Index]= 0

        previous_day = day


def body_outside_band_system(price_data, period1=20, bandwidth=1, profit_target=6, trailing_stop=2, period="",
                             trade_type="Both_leg", underlying_instrument_data=None):
    trailing_stop = - trailing_stop / 100
    profit_target = profit_target / 100
    bandwidth = bandwidth / 100
    period_ema = str(period1) + "_EMA"

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    ema.ema(price_signal_period, period1)
    price_signal_period["Upper_band"] = price_signal_period[period_ema] * (1 + (bandwidth))
    price_signal_period["Lower_band"] = price_signal_period[period_ema] * (1 - (bandwidth))

    price_signal_period["Trade_signal"] = np.where(
        price_signal_period["Low"] > price_signal_period["Upper_band"].shift(), 1,
        np.where(price_signal_period["High"] < price_signal_period["Lower_band"].shift(), -1, 0))

    price_signal_period["Signal"] = 0

    signal_generation(price_signal_period, profit_target, trailing_stop)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal
