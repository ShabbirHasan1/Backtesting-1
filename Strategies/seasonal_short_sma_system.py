import numpy as np

from Technical_Indicators import sma as sma
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

def signal_generation(price_signal_period,entry_date,exit_date):

    for i in price_signal_period.index:
        if i==price_signal_period.index[0]:
            previous_day=i
            price_signal_period["signal"]=0
            continue

        if (i.day > entry_date) and (previous_day.day<=entry_date):
            price_signal_period["signal"] = price_signal_period[previous_day]["sma_signal"]
        elif (i.day > exit_date) and (previous_day.day<=exit_date):
            price_signal_period["signal"] = 0
        else:
            price_signal_period["signal"] = np.nan
        previous_day=i

    return price_signal_period["signal"]


def seasonal_short_sma_system(price_data,period_sma=10,entry_date=16,exit_date=22,period="", trade_type="Both_leg", underlying_instrument_data=None):

    period=""

    period_str=str(period_sma)+"_SMA"

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    price_signal_period = price_period
    price_signal = price_data

    sma.sma(price_signal_period, period_sma)

    price_signal_period["sma_signal"]=np.where(price_signal_period["Close"]<price_signal_period[period_str],-1,0)

    price_signal_period["Signal"] = signal_generation(price_signal_period,entry_date,exit_date)
    price_signal_period["Signal"].fillna(method="ffill",inplace=True)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"] = price_signal["Signal"].shift(1)
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)
    price_signal["Trades"].fillna(0, inplace=True)



    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal, "Close")

    return trades, price_signal
