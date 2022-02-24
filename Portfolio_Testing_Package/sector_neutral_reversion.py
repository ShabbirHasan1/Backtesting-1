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

def creating_portfolio(cash_price_data,nifty_data,universe_stocks,trade_days,universal_dates,universe_sector_data,sectors):

    cash_symbols_data_list=pd.Series(cash_price_data.keys())
    expiry_days=trade_days

    universe_stocks_daily=creating_universe(universe_stocks,universal_dates)
    expiry_days_stocks=universe_stocks_daily.loc[expiry_days.tolist()]
    universe_sector_data.set_index("Company",inplace=True)

    this_expiry_close_price=pd.DataFrame(0,columns=cash_symbols_data_list,index=expiry_days)

    buy_portfolio=pd.DataFrame()
    sell_portfolio=pd.DataFrame()

    for stock in cash_symbols_data_list:
        this_expiry_close_price[stock]=cash_price_data[stock]["Close"]

    this_expiry_close_price.ffill(inplace=True)
    this_expiry_close_price.fillna(0,inplace=True)
    expiry_returns=(this_expiry_close_price/this_expiry_close_price.shift(1))-1
    expiry_returns.fillna(0,inplace=True)

    for expiry_day in expiry_days[1:]:

        monthly_universe=expiry_days_stocks.loc[expiry_day]
        monthly_universe.dropnna(inplace=True)
        monthly_universe=monthly_universe[monthly_universe!="TTMT/A IN Equity"]
        monthly_universe=monthly_universe.to_frame().reset_index()
        monthly_universe.drop(["index"],axis=1,inplace=True)
        monthly_universe.set_index(monthly_universe.columns[0],inplace=True)

        monthly_universe["Sector"]=universe_sector_data["Sector"]

        monthly_universe=monthly_universe[monthly_universe["Sector"].isin(sectors)]

        monthly_universe["Returns"]=expiry_returns.loc[expiry_day]
        monthly_universe.dropna(inplace=True)

        buy_p = pd.DataFrame()
        sell_p = pd.DataFrame()

        for sector in sectors:
            sector_universe=monthly_universe[monthly_universe["Sector"]==sector]
            buy_sector=pd.DataFrame(sector_universe["Returns"].astype(float).nsmallest(2,keep="all").index)
            sell_sector = pd.DataFrame(sector_universe["Returns"].astype(float).nlargest(2, keep="all").index)
            buy_p=pd.concat([buy_p,buy_sector],ignore_index=True)
            sell_p = pd.concat([sell_p, sell_sector], ignore_index=True)

        buy_portfolio=buy_portfolio.append(buy_p.T)
        sell_portfolio=sell_portfolio.append(sell_p.T)

    return buy_portfolio,sell_portfolio


if __name__=="__main__":
    warnings.filterwarnings("ignore")

    input_folder_path=Path().absolute().joinpath("Input_files")
    current_folder_path=Path().absolute().joinpath("Data")
    expiry_days_path=current_folder_path/"Expiry days.csv"
    universe_stocks_path=current_folder_path/"BSE100 Index for SN.csv"
    universe_sector_path=current_folder_path/"BSE100 GICS Sector for SN.csv"
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
    universe_sector_data=pd.read_csv(universe_sector_path)
    sectors=["IT","Energy","Financial","Pharma","Consumer"]

    buy_portfolio,sell_portfolio = creating_portfolio(cash_price_data, nifty_data, universe_stocks,expiry_days, universal_dates,universe_sector_data,sectors)

    buy_portfolio.name="Buy Portfolio"
    sell_portfolio.name="Sell Portfolio"

    to_be_saved_as_file=[buy_portfolio,sell_portfolio]
    my_funcs.excel_creation(to_be_saved_as_file,"Portfolio Results/Sector Neutral","Sector Neutral Results")


