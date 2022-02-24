import pandas as pd
import numpy as np
from pathlib import Path
import my_funcs
import datetime
import warnings

def creating_universe(combined_portfolio_list,dates):
    combined_portfolio_list=combined_portfolio_list.T
    combined_portfolio_list=combined_portfolio_list.replace({" IS ":" IN "},regex=True)
    combined_portfolio_list.index=pd.to_datetime(combined_portfolio_list.index)
    universe_daily_stocks=combined_portfolio_list.reindex(dates,method='ffill')

    return universe_daily_stocks

def creating_portfolio(cash_price_data,nifty_data,universe_stocks,trade_days,universal_dates):

    cash_symbols_data_list=pd.Series(cash_price_data.keys())
    universe_stocks_daily=creating_universe(universe_stocks,universal_dates)
    daily_close_price=pd.DataFrame(0,columns=cash_symbols_data_list,index=universal_dates)

    buy_portfolio=pd.DataFrame()
    sell_portfolio=pd.DataFrame()
    daily_universe=pd.DataFrame()
    daily_universe_portfolios=pd.DataFrame()

    for stock in cash_symbols_data_list:
        daily_close_price[stock]=cash_price_data[stock]["Close"]

    daily_close_price.ffill(inplace=True)
    daily_close_price.fillna(0,inplace=True)

    daily_returns=(daily_close_price/daily_close_price.shift(1))-1
    daily_returns.fillna(0,inplace=True)

    for day in universal_dates:
        todays_universe=universe_stocks_daily.loc[day]
        todays_universe.dropnna(inplace=True)
        todays_universe=todays_universe[todays_universe!="TTMT/A IN Equity"]
        todays_universe=todays_universe.to_frame().reset_index()
        todays_universe["Returns"]=0
        todays_universe.drop(["index"],axis=1,inplace=True)
        todays_universe.set_index(todays_universe.columns[0],inplace=True)

        todays_returns=daily_returns.loc[day]
        todays_universe["Returns"]=todays_returns

        buy_p=pd.DataFrame(todays_universe["RSI"].astype(float).nsmallest(10,keep="all").index)
        sell_p = pd.DataFrame(todays_universe["RSI"].astype(float).nlargest(10, keep="all").index)

        buy_portfolio=buy_portfolio.append(buy_p.T)
        sell_portfolio=sell_portfolio.append(sell_p.T)
        daily_universe=daily_universe.append(todays_universe.T)
        daily_universe_portfolios=daily_universe_portfolios.append(pd.DataFrame(todays_universe.index).T)

    buy_portfolio["Day"]=universal_dates
    buy_portfolio.set_index("Day",inplace=True)
    buy_portfolio=buy_portfolio.iloc[1:,:]
    buy_portfolio=buy_portfolio.shift(1,fill_value="")


    sell_portfolio["Day"]=universal_dates
    sell_portfolio.set_index("Day",inplace=True)
    sell_portfolio=sell_portfolio.iloc[1:,:]
    sell_portfolio=sell_portfolio.shift(1,fill_value="")

    daily_universe["Day"]=universal_dates
    daily_universe.set_index("Day",inplace=True)
    daily_universe_portfolios["Day"]=universal_dates
    daily_universe_portfolios.set_index("Day",inplace=True)

    return buy_portfolio,sell_portfolio,daily_universe_portfolios,daily_universe


if __name__=="__main__":
    warnings.filterwarnings("ignore")

    input_folder_path=Path().absolute().joinpath("Input_files")
    current_folder_path=Path().absolute().joinpath("Data")
    expiry_days_path=current_folder_path/"Expiry days.csv"
    universe_stocks_path=current_folder_path/"Nifty Index members.csv"
    nifty_price_data_path=current_folder_path/"Price_Data/Nifty Index.csv"
    futures_1_data_folder_path=current_folder_path/"Futures Prices CSV"
    cash_data_folder_path=current_folder_path/"Stock Prices CSV"

    portfolio_start_date = datetime.datetime(2010,12,1)
    portfolio_end_date = datetime.datetime(2022, 2, 28)

    nifty_data=my_funcs.reading_price_data_from_csv(nifty_price_data_path)
    universal_dates= nifty_data.index[(nifty_data.index>portfolio_start_date) &(nifty_data.index<=portfolio_end_date) ]

    monthly_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="M")
    annual_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="Y")

    cash_price_data=my_funcs.import_all_price_data_from_csv_files(cash_data_folder_path)
    cash_symbol_data_list=pd.Series(cash_price_data.keys())

    futures_1_price_data=my_funcs.import_all_price_data_from_csv_files(futures_1_data_folder_path)
    futures_1_symbol_data_list=pd.Series(futures_1_price_data.keys())

    expiry_days=pd.read_csv(expiry_days_path)
    expiry_days=pd.to_datetime(expiry_days["Expiry days"])
    expiry_days=expiry_days[expiry_days.between(portfolio_start_date,portfolio_end_date)]
    universe_stocks=pd.read_csv(universe_stocks_path)

    buy_portfolio,sell_portfolio,daily_universe_portfolios,daily_universe = creating_portfolio(cash_price_data, nifty_data, universe_stocks,expiry_days, universal_dates)

    buy_portfolio.name="Buy Portfolio"
    sell_portfolio.name="Sell Portfolio"
    daily_universe.name="Daily Returns"
    daily_universe_portfolios.name="Daily Universe"

    to_be_saved_as_file=[buy_portfolio,sell_portfolio,daily_universe,daily_universe_portfolios]
    my_funcs.excel_creation(to_be_saved_as_file,"Portfolio Results/DailyMR","DailyMR Results")


