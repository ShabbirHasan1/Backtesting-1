import math
import pandas as pd
import numpy as np
from Technical_Indicators import rsc as rsc
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

def creating_portfolio(cash_price_data,universe_stocks,trade_days,universal_dates,period=10):

    cash_symbols_data_list=pd.Series(cash_price_data.keys())

    buy_portfolio=pd.DataFrame()
    sell_portfolio=pd.DataFrame()
    RSC_universe=pd.DataFrame()
    monthly_universe_portfolios=pd.DataFrame()
    daily_rsc=pd.DataFrame(0,columns=cash_symbols_data_list,index=universal_dates)


    universe_stocks_daily=creating_universe(universe_stocks,universal_dates)
    expiry_days_stocks=universe_stocks_daily.loc[trade_days.tolist()]

    for stock in cash_symbols_data_list:

        daily_rsc[stock]=rsc.rsc(cash_price_data[stock],nifty_data,period)


    for expiry_day in expiry_days_stocks.index:

        monthly_universe=expiry_days_stocks.loc[expiry_day]
        monthly_universe.dropnna(inplace=True)
        monthly_universe=monthly_universe[monthly_universe!="TTMT/A IN Equity"]
        monthly_universe=monthly_universe.to_frame().reset_index()
        monthly_universe["RSI"]=0
        monthly_universe.drop(["index"],axis=1,inplace=True)
        monthly_universe.set_index(monthly_universe.columns[0],inplace=True)

        rsc_numbers=daily_rsc.loc[expiry_day]
        monthly_universe["RSC"]=rsc_numbers

        buy_p=pd.DataFrame(monthly_universe["RSC"].astype(float).nsmallest(10,keep="all").index)
        sell_p = pd.DataFrame(monthly_universe["RSC"].astype(float).nlargest(10, keep="all").index)

        buy_portfolio=buy_portfolio.append(buy_p.T)
        sell_portfolio=sell_portfolio.append(sell_p.T)
        RSC_universe=RSC_universe.append(monthly_universe.T)
        monthly_universe_portfolios=monthly_universe_portfolios.append(pd.DataFrame(monthly_universe.index).T)

    buy_portfolio["expiry_days"]=expiry_days_stocks.index
    buy_portfolio.set_index("expiry_days",inplace=True)
    sell_portfolio["expiry_days"]=expiry_days_stocks.index
    sell_portfolio.set_index("expiry_days",inplace=True)
    RSC_universe["expiry_days"]=expiry_days_stocks.index
    RSC_universe.set_index("expiry_days",inplace=True)
    monthly_universe_portfolios["expiry_days"]=expiry_days_stocks.index
    monthly_universe_portfolios.set_index("expiry_days",inplace=True)

    return buy_portfolio,sell_portfolio,monthly_universe_portfolios,RSC_universe


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

    buy_portfolio,sell_portfolio,monthly_universe_portfolios,RSC_universe = creating_portfolio(cash_price_data, universe_stocks, expiry_days, universal_dates,10)

    buy_portfolio.name="Buy Portfolio"
    sell_portfolio.name="Sell Portfolio"
    RSC_universe.name="RSC reversion"
    monthly_universe_portfolios.name="Monthly Universe"

    to_be_saved_as_file=[buy_portfolio,sell_portfolio,RSC_universe,monthly_universe_portfolios]
    my_funcs.excel_creation(to_be_saved_as_file,"Portfolio Results/RSC reversion","RSC_Nifty")


