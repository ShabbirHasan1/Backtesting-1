# Creating oscillator indicator

# input: Price_data: Date, Open, High, Low, Close, Volume;

# Output: Oscillator indicator
import pandas as pd

from Technical_Indicators import sma, atr

def oscillator(price_data):

    sma_diff=price_data["Close"]-sma.sma(price_data,24)
    ATR=atr.atr(price_data,24)
    oscillator=sma_diff/ATR
    price_data["Oscillator"]=oscillator

    return oscillator
