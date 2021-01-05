from Technical_Indicators import sma as sma
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_generation as tc
from Trade_Generation import creating_individual_trade

import numpy as np
from numpy_ext import rolling_apply
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression


def regression_crossover_system(price_data, period1=10, period2=5, period3=50, period="", trade_type="Both_leg",
                                underlying_instrument_data=None):
    period_sma = str(period1) + "_SMA"

    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    sma.sma(price_period, period1)

    price_signal_period = price_period

    price_signal = price_data

    price_signal_period["row_number"] = np.arange(1, len(price_signal_period) + 1)
    price_signal_period["d5_LS"] = rolling_apply(get_slope, period2, price_signal_period["Close"],
                                                 price_signal_period["row_number"])
    price_signal_period["d5_LS"].fillna(0, inplace=True)

    price_signal_period["d50_LR"] = rolling_apply(regress_predict, period3, price_signal_period["row_number"],
                                                  price_signal_period["d5_LS"])
    price_signal_period["d50_LR"].fillna(0)

    price_signal_period["Signal"] = np.where((price_signal_period["Close"] > price_signal_period[period_sma]) &
                                             (price_signal_period["d5_LS"] > price_signal_period["d50_LR"]), 1,
                                             np.where(
                                                 (price_signal_period["Close"] < price_signal_period[period_sma]) &
                                                 (price_signal_period["d5_LS"] < price_signal_period["d50_LR"]), -1, 0))

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, underlying_instrument_data)
    else:
        trades = tc.trade_generation(price_signal)

    return trades, price_signal


def get_slope(y, x):
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    return slope


def regress_predict(x, y):
    x = np.array(x)
    x = x.reshape(-1, 1)

    model = LinearRegression()
    model.fit(x, y)

    X_predict = x[-1].reshape(-1, 1)
    Y_predict = model.predict(X_predict)

    return Y_predict[0]
