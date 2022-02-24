import pandas as pd
import numpy as np
from pathlib import Path
import my_funcs
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    #enter the file to upload data
    folder_path = Path().absolute().joinpath("Data")
    file_name = "Futures_price_data"

    file_path = folder_path .joinpath(file_name+".csv")
    price_data = pd.read_csv(file_path)

    stocks = price_data.iloc[0]
    stocks.dropna(inplace=True)
    stocks = stocks.apply(lambda x:x if "=" not in x else np.nan)
    stocks.dropna(inplace=True)
    base_index = stocks[0]
    stocks = stocks[2:]

    price_data = price_data[2:].iloc[:, 6:]
    a=len(price_data.columns)
    price_data.columns=range(len(price_data.columns))

    stock_prices =[]

    for stock in stocks:
        stock_df = price_data.iloc[:, :6]
        stock_df.columns = ["Dates","Open","High","Low","Close","Volume"]

        stock_df.dropna(subset=["Dates"], inplace=True)

        stock_df.set_index("Dates", inplace=True)
        stock_df.index = pd.to_datetime(stock_df.index, format="%d-%m-%Y")
        stock_df.name = stock


        stock_df["Close"].fillna(method="ffill",inplace=True)
        stock_df["Volume"].fillna(0,inplace=True)
        stock_df.fillna(axis=1,method="bfill",inplace=True)
        price_data = price_data.iloc[:,6:]
        stock_prices.append(stock_df)

    my_funcs.csv_creation(stock_prices, folder_path.joinpath("Futures prices CSV"))

