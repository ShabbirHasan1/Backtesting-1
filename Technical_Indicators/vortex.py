# Creating vortex indicator

# input: Price_data: Date, Open, High, Low, Close, Volume;

# Output: vortex indicator
import pandas as pd


def vortex(price_data):

    vm_plus=abs(price_data["High"]-price_data["Low"].shift())
    vm_minus = abs(price_data["Low"] - price_data["High"].shift())
    vzm_plus=vm_plus.rolling(14).sum()
    vzm_minus = vm_minus.rolling(14).sum()

    high = price_data["High"]
    low = price_data["Low"]
    close = price_data["Close"]
    tr0 = abs(high - low)
    tr1 = abs(high - close.shift())
    tr2 = abs(low - close.shift())
    tr = pd.concat([tr0,tr1,tr2],axis=1)
    tr_1 = tr.max(axis=1)

    tr14=tr_1.rolling(14).sum()
    vi14_plus=vzm_plus/tr14
    vi14_minus=vzm_minus/tr14

    vortex=vi14_plus-vi14_minus
    vortex.fillna(0,inplace=True)
    price_data["Vortex"]=vortex

    data_check=pd.concat([vm_plus,vm_minus,vzm_plus,vzm_minus,tr14,vi14_plus,vi14_minus,vortex],axis=1)
    data_check.to_csv("data_check.csv",header=True,index=True)

    return vortex
