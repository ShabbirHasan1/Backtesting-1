import numpy as np

from Technical_Indicators import sma as sma
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

def signal_generation(price_signal_period,entry_date,exit_date):


    days=price_signal_period.itertuples()
    next_day=price_signal_period.itertuples()
    next(next_day)

    for row in days:
        if row.Index == price_signal_period.index[-1]:
            break
        else:
            next_day_values=next(next_day)
            if next_day_values.Index.day>entry_date:
                entry_month = row.Index.month

                if row.sma_signal==-1:
                    if entry_date<exit_date:
                        while next_day_values.Index.month==entry_month:
                            if next_day_values.Index.day<=exit_date:
                                price_signal_period["Signal"][row.Index] = -1
                            else:
                                price_signal_period["Signal"][row.Index] = 0
                            row=next(days)
                            next_day_values=next(next_day)
                    else:
                        while True:
                            if ((next_day_values.Index.day>exit_date) and (next_day_values.Index.month!=entry_month)):
                                price_signal_period["Signal"][row.Index] = 0
                                break
                            price_signal_period["Signal"][row.Index] = -1
                            row=next(days)
                            next_day_values=next(next_day)
                else:
                    while (next_day_values.Index.month==entry_month):
                        price_signal_period["Signal"][row.Index] = 0
                        row=next(days)
                        next_day_values = next(next_day)
            else:
                price_signal_period["Signal"][row.Index] = 0

    return price_signal_period["Signal"]


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

    price_signal_period["Signal"]=np.nan
    price_signal_period["Signal"] = signal_generation(price_signal_period,entry_date,exit_date)
    price_signal_period["Signal"].fillna(method="ffill",inplace=True)

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)
    price_signal["Trades"].fillna(0, inplace=True)



    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Close"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal, "Close")

    return trades, price_signal
