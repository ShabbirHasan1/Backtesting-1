import pandas as pd
import numpy as np

def position_size(price_data,baseamount):

    position_size = pd.DataFrame(0, index=price_data.index, columns=["Position Size"])

    position_size["Position Size"] = ((baseamount/price_data["Close"].shift(1)))
    position_size["Position Size"][0] = baseamount/price_data["Open"][0]
    position_size["Position Size"]=position_size["Position Size"].apply(np.floor)

    position_size["Month"] = position_size.index.month

    position_size["EOM"] = (position_size["Month"] == position_size["Month"].shift(1))

    position_size["Positions"] = position_size.apply(lambda x: x["Position Size"] if not x["EOM"] else 0, axis=1)

    position_size["Positions"].replace(to_replace=0, method="ffill", inplace=True)

    position_size = position_size["Positions"].shift(-1).fillna(method="ffill")


    return position_size


