import numpy as np
import pandas as pd
import datetime
from pathlib import Path
import my_funcs as my_funcs
from Timeframe_Manipulation import series_resampling as series_re

def trade_creation(portfolio_type,portfolio_strategy,long_portfolio,short_portfolio,next_series_data,price_data,
                   nifty_data,expiry_days):

    trade_not_found=pd.DataFrame(columns=["Stock","Date","Buy/Sell"])

    buy_trade_list=pd.DataFrame(columns=["Account","Strategy","Date","Price","Side","Contract","Underlying","Contract_type","Qty",
                   "Trading_Cost","Strike_Price"])

    for date in long_portfolio.index:

        trades=long_portfolio.loc[date]
        trades.dropna(inplace=True)

        for stock in trades:
            try:
                if date in expiry_days:
                    stock_data=next_series_data[stock]
                else:
                    stock_data=price_data[stock]

                price=stock_data.loc[date,"Close"]

                buy_trade_list.loc[len(buy_trade_list.index)]=[portfolio_type,portfolio_strategy,date,price,1,stock,stock,"F",1,0,0]

            except:
                trade_not_found.loc[len(trade_not_found.index)]=[stock,date,"Buy"]
                price=nifty_data.loc[date,"Close"]
                buy_trade_list.loc[len(buy_trade_list.index)]=[portfolio_type,portfolio_strategy,date,price,1,"Nz1 Index",stock,"F",1,0,0]

    sell_trade_list = pd.DataFrame(
        columns=["Account", "Strategy", "Date", "Price", "Side", "Contract", "Underlying", "Contract_type", "Qty",
                 "Trading_Cost", "Strike_Price"])

    for date in short_portfolio.index:

        trades = short_portfolio.loc[date]
        trades.dropna(inplace=True)

        for stock in trades:
            try:
                if date in expiry_days:
                    stock_data = next_series_data[stock]
                else:
                    stock_data = price_data[stock]

                price = stock_data.loc[date, "Close"]

                sell_trade_list.loc[len(sell_trade_list.index)] = [portfolio_type, portfolio_strategy, date, price, -1,
                                                                 stock, stock, "F", 1, 0, 0]

            except:
                trade_not_found.loc[len(trade_not_found.index)] = [stock, date, "Sell"]
                price = nifty_data.loc[date, "Close"]
                sell_trade_list.loc[len(sell_trade_list.index)] = [portfolio_type, portfolio_strategy, date, price, -1,
                                                                 "Nz1 Index", stock, "F", 1, 0, 0]

    trade_list=buy_trade_list.append(sell_trade_list)

    return trade_list,trade_not_found


if __name__=="__main__":
    portfolio_type="Mean reversion"
    portfolio_strategy="SML"

    current_folder_path=Path().absolute().joinpath("Data")
    data_folder_path_cash=Path().absolute().joinpath("Data/Cash prices CSV")
    data_folder_path_futures2=Path().absolute().joinpath("Data/New Futures prices series2 CSV")
    nifty_price_data_path=Path().absolute().joinpath("Data/Price_Data/Nz1 Index.csv")
    expiry_days_path=current_folder_path/"Expiry days.csv"
    buy_trade_file=current_folder_path/"Portfolio_construction/SML/SML_buy_trades.csv"
    sell_trade_file=current_folder_path/"Portfolio_construction/SML/SML_sell_trades.csv"

    nifty_data=my_funcs.reading_price_data_from_csv(nifty_price_data_path)
    universal_dates=nifty_data.index

    price_data=my_funcs.import_all_price_data_from_csv_files(data_folder_path_cash)
    price_data_futures2=my_funcs.import_all_price_data_from_csv_files(data_folder_path_futures2)

    symbols_data=price_data.keys()

    monthly_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="M")
    annual_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="Y")

    buy_trades=pd.read_csv(buy_trade_file)
    buy_trades.set_index("Dates",inplace=True)
    buy_trades.index=pd.to_datetime(buy_trades.index)
    sell_trades=pd.read_csv(sell_trade_file)
    sell_trades.set_index("Dates",inplace=True)
    sell_trades.index=pd.to_datetime(sell_trades.index)


    expiry_days=pd.read_csv(expiry_days_path)
    expiry_days=pd.to_datetime(expiry_days["Expiry days"])
    expiry_days=expiry_days[expiry_days.between(buy_trades.index[0],buy_trades.index[-1])]



    nifty_monthly=series_re.price_series_periodic(nifty_data,"M")
    month_end_date=nifty_monthly.index

    trade_list, trade_not_found=trade_creation(portfolio_type,portfolio_strategy,buy_trades,sell_trades,price_data_futures2,price_data,
                   nifty_data,expiry_days)

    trade_list.name='trade list'
    trade_not_found.name='trades not found'
    to_be_saved_as_csv=[trade_list,trade_not_found]

    my_funcs.csv_creation(to_be_saved_as_csv,current_folder_path/"Portfolio_construction/SML")