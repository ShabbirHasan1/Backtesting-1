from Technical_Indicators import oscillator as oscillator
from Timeframe_Manipulation import series_resampling as series_resampling
from Trade_Generation import trade_close as tc
from Trade_Generation import creating_individual_trade

previous_signal = 0

def oscillator_system(price_data, period="", trade_type="Both_leg", underlying_instrument_data=None):
    if period == "":
        price_period = price_data
    else:
        price_period = series_resampling.price_series_periodic(price_data, period)

    oscillator.oscillator(price_period)

    price_signal_period = price_period
    price_signal = price_data

    price_signal_period["Signal"] = price_signal_period["Oscillator"].apply(signal_generator)

    # price_signal_period["Signal"] = np.where((price_signal_period["Oscillator"] >= 1), 1,
    #                                  np.where((price_signal_period["Oscillator"] <= -1), -1, 0))

    price_signal["Signal"] = price_signal_period["Signal"].resample("D").ffill()
    price_signal["Signal"] = price_signal["Signal"].shift(1)
    price_signal["Signal"].fillna(0, inplace=True)

    price_signal["Trades"] = price_signal["Signal"] - price_signal["Signal"].shift(1)
    price_signal["Trades"].fillna(0, inplace=True)

    if trade_type == "Individual":
        trades = creating_individual_trade.creating_individual_trade(price_signal, price_signal["Open"],
                                                                     underlying_instrument_data)
    else:
        trades = tc.trade_close(price_signal, "Open")

    return trades, price_signal


def signal_generator(oscillator):
    global previous_signal

    if oscillator > 1:
        signal = 1
        previous_signal = signal
    elif oscillator < -1:
        signal = -1
        previous_signal = signal
    else:
        if previous_signal == -1 and oscillator > 0:
            signal = 0
            previous_signal = 0
        elif previous_signal == 1 and oscillator < 0:
            signal = 0
            previous_signal = 0
        else:
            signal = previous_signal

    return signal
