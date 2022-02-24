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
    universe_stocks_daily["Week_Number"]=universe_stocks_daily.index.strftime("%U-%Y")
    universe_stocks_daily["Date"]=universe_stocks_daily.index

    weekly_stocks=universe_stocks_daily.groupby(["Week_Number"]).last()

    expiry_days=pd.DataFrame(0,columns=["Week_Number"],index=trade_days)
    expiry_days["Week_Number"]=expiry_days.index.strftime("%U-%Y")
    expiry_days["Date"]=expiry_days.index
    expiry_days.set_index("Week_Number",inplace=True)

    weekly_stocks.update(expiry_days)
    weekly_stocks.set_index("Date",inplace=True)

    this_week_close_price=pd.DataFrame(0,columns=cash_symbols_data_list,index=weekly_stocks.index)

    buy_portfolio=pd.DataFrame()
    sell_portfolio=pd.DataFrame()
    weekly_universe=pd.DataFrame()
    weekly_universe_portfolios=pd.DataFrame()

    for stock in cash_symbols_data_list:
        this_week_close_price[stock]=cash_price_data[stock]["Close"]

    this_week_close_price.ffill(inplace=True)
    this_week_close_price.fillna(0,inplace=True)
    weekly_returns=(this_week_close_price/this_week_close_price.shift(1))-1
    weekly_returns.fillna(0,inplace=True)

    for weekly_dates in weekly_returns.index:
        this_week_universe=weekly_stocks.loc[weekly_dates]
        this_week_universe.dropnna(inplace=True)
        this_week_universe=this_week_universe[this_week_universe!="TTMT/A IN Equity"]
        this_week_universe=this_week_universe.to_frame().reset_index()
        this_week_universe["Returns"]=0
        this_week_universe.drop(["index"],axis=1,inplace=True)
        this_week_universe.set_index(this_week_universe.columns[0],inplace=True)

        this_week_returns=weekly_returns.loc[weekly_dates]
        this_week_universe["Returns"]=this_week_returns

        buy_p=pd.DataFrame(this_week_universe["Returns"].astype(float).nsmallest(10,keep="all").index)
        sell_p = pd.DataFrame(this_week_universe["Returns"].astype(float).nlargest(10, keep="all").index)

        buy_portfolio=buy_portfolio.append(buy_p.T)
        sell_portfolio=sell_portfolio.append(sell_p.T)
        weekly_universe=weekly_universe.append(this_week_universe.T)
        weekly_universe_portfolios=weekly_universe_portfolios.append(pd.DataFrame(this_week_universe.index).T)

    buy_portfolio["week_end_days"]=weekly_returns.index
    buy_portfolio.set_index("week_end_days",inplace=True)

    sell_portfolio["week_end_days"]=weekly_returns.index
    sell_portfolio.set_index("week_end_days",inplace=True)

    weekly_universe["week_end_days"]=weekly_returns.index
    weekly_universe.set_index("week_end_days",inplace=True)
    weekly_universe_portfolios["week_end_days"]=weekly_returns.index
    weekly_universe_portfolios.set_index("week_end_days",inplace=True)

    return buy_portfolio,sell_portfolio,weekly_universe_portfolios,weekly_universe


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

    weekly_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="W")
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

    buy_portfolio,sell_portfolio,weekly_universe_portfolios,weekly_universe = creating_portfolio(cash_price_data, nifty_data, universe_stocks,expiry_days, universal_dates)

    buy_portfolio.name="Buy Portfolio"
    sell_portfolio.name="Sell Portfolio"
    weekly_universe.name="Weekly Returns"
    weekly_universe_portfolios.name="Weekly Universe"

    to_be_saved_as_file=[buy_portfolio,sell_portfolio,weekly_universe,weekly_universe_portfolios]
    my_funcs.excel_creation(to_be_saved_as_file,"Portfolio Results/WeeklyMR","WeeklyMR Results")


