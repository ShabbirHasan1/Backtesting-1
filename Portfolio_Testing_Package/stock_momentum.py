import datetime
import pandas as pd

from Independent_programs import single_instrument_single_system as si
from PNL_Generation import pnl_generation as pg
from pathlib import Path

from Strategies import *
from Trade_Analysis import trade_distribution,trade_summary,rolling_12m_trade_summary
from Trade_Analysis import walkforward_annual_summary

from dateutil.relativedelta import *
from my_funcs import *
import warnings

def saving_dataframes(portfolio_values,name):
    portfolio_values.name=name
    to_be_saved_as_csv=[portfolio_values]
    excel_creation(to_be_saved_as_csv,"Portfolio_PNL/Iterations/Stock_Momentume",name)

def creating_trades(strategy,period,parameters,price_data):
    parameters=list(filter(None,parameters))

    method_name=strategy
    method=eval(method_name)

    strategy_func=getattr(method,strategy)
    if period is None: period=""

    trades,price_signal=strategy_func(price_data,*parameters,period=period,trade_type="Individual")

    print(f"{strategy}--ok!")

    return trades,price_signal

def internamedtuples_unpack(strategies_data):
    strategy=namedtuple("strategy",["Symbol","Strategy","Period","Parameters"])
    strategy_list=[]
    symbol=[]

    for row in strategies_data.index:
        strategy_symbol=strategies_data.loc[row][0]
        strategy_name=strategies_data.loc[row][1]
        period=strategies_data.loc[row][2]

        strategy_1=strategy(strategy_symbol,strategy_name,period,strategies_data.loc[row][3:].tolist())

        print(f"{row}--{strategy_name}")
        strategy_list.append(strategy_1)
        symbol.append(strategy_symbol)

    return symbol,strategy_list

def creating_single_leg_trades(strategies_data,data_path,nifty_data,start_date=datetime.datetime(2010,11,30),end_date=datetime.datetime(2022,2,31)):

    trades=pd.DataFrame()

    start_date_stocks=start_date+relativedelta(months=-6)
    symbols,strategy_list=internamedtuples_unpack(strategies_data)
    price_data=import_price_data_from_csv_files(data_path,symbols)

    universal_dates=nifty_data.index
    universal_dates=universal_dates[universal_dates>start_date]

    for strategy in strategy_list:

        price_data_symbol=price_data[strategy.Symbol].copy()
        price_data_symbol=price_data_symbol.loc[price_data_symbol.index>start_date_stocks]

        try:
            trades_1,price_sugnal=creating_trades(strategy.Strategy,strategy.Period,strategy.Prameters,price_data_symbol)

            trades_1.Contract=strategy.Symbol
            trades_1.Contract_Type="F"
            trades_1.Trading_Cost=0
            trades_1.Strike_Price=0
            trades_1.dropna(inplace=True)
            trades_1.reset_index(drop=True,insplace=True)
            trades_1["Underlying"]=trades_1["Contract"]
            trades_1["Strategy"]=strategy.Strategy

            trades_1=trades_1[trades_1["Date"]>start_date]
            trades_1.reset_index(inplace=True,drop=True)
            if trades_1.loc[0,"Qty"]==2:
                trades_1.loc[0,"Qty"]=1
            pos=trades_1["Side"]*trades_1["Qty"]
            if pos.sum()!=0:
                trades_1=trades_1.iloc[1:,:]

            trades=trades.append(trades_1,ignore_index=True)
        except:
            print(f"{strategy.Strategy} NOT OK!!!!!!!!!")

    trades["Account"]=trades["Strategy"]
    trades["Strategy"]="Stock_Momentum"

    trades=trades[["Account","Strategy","Date","Price","Side","Contract","Underlying","Contract_type","Qty",
                   "Trading_Cost","Strike_Price"]]

    return trades

if __name__=="__main__":
    warnings.filterwarnings("ignore")

    folder_path=Path().absolute().joinpath("Input_files")
    data_path=Path().absolute().joinpath("Data/New Futures prices CSV")
    nifty_price_data_path=Path().absolute().joinpath("Data/Price_Data/Nz1 Index.csv")

    start_date=datetime.datetime(2010,11,30)
    end_date=datetime.datetime(2022,2,28)

    input_file_name="Strategies.xlsx"
    input_file=folder_path/input_file_name

    strategies=read_from_excel(input_file)

    straties_data=strategies["Strategies"]
    straties_data.reset_index(inplace=True)

    nifty_data=reading_price_data_from_csv(nifty_price_data_path)

    trades=creating_single_leg_trades(straties_data,data_path,nifty_data,start_date,end_date)

    trades.name="Trades"

    to_be_saved_as_csv=[trades]

    excel_creation(to_be_saved_as_csv,"Data/Portfolio_construction","Stock_Momentum")




