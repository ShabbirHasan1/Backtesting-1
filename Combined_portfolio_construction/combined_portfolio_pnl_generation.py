import datetime

import numpy as np
import pandas as pd
from Individual_Trades import Individual_Trades
from my_funcs import *
import warnings

def combined_portfolio_pnl_generation(universal_dates,expiry_days,baseamount,exposure_limit,strategy_detaions,price_data,
                                      futures_2_data,individual_trade_list,output_folder):
    previous_day_AUM=baseamount
    monthly_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="M")
    expiry_days=pd.to_datetime(expiry_days)
    stock_momentum_hedge_required=0
    current_stock_momentum_hedge=0

    account_list=individual_trade_list["Account"].unique()
    strategy_list=individual_trade_list["Strategy"].unique()
    symbols=individual_trade_list["Contract"].unique()
    symbols=np.append(symbols,"Nz1 Index") if "Nz1 Index" not in symbols else symbols
    symbols_1=pd.Series(symbols)

    individual_trade_list.sort_values(by=["Date","Contract"],ignore_index=True,inplace=True)
    individual_trade_list["Qty"]=individual_trade_list["Qty"].astype(float)
    individual_trade_list["Side"]=individual_trade_list["Side"].astype(float)

    symbols_data_list=pd.Series(price_data.keys())
    todays_trade=pd.DataFrame(columns=individual_trade_list.columns)
    strategy_exit_trades=pd.DataFrame(columns=individual_trade_list.columns)

    #checking if any symbol data is unavailable
    symbols_data_unavailable=symbols_1[~symbols_1.isin(symbols_data_list)]


    if ~pd.isnull(symbols_data_unavailable).all():
        print(f"Following symbols data not found \n"
              f"{symbols_data_unavailable[symbols_data_unavailable.notnull()]}")
        quit()
    else:
        print("=====ALL DATA FOUND====")

    #creating dictionary for strategy master data
    strategy_data={}

    strategy_data["RSI"]={}
    strategy_data["RSI"]["Strategy"]="RSI"
    strategy_data["RSI"]["Positions"]=pd.DataFrame(0,
        columns=["QTY","Side","Entry_price","Todays_price","Yesterdays_price","Todays_PNL","Trade_PNL"])
    strategy_data["RSI"]["Trade_PNL"]=0
    strategy_data["RSI"]["Todays_PNL"]=0

    strategy_data["RSC"] = {}
    strategy_data["RSC"]["Strategy"] = "RSC"
    strategy_data["RSC"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["RSC"]["Trade_PNL"] = 0
    strategy_data["RSC"]["Todays_PNL"] = 0

    strategy_data["ESA"] = {}
    strategy_data["ESA"]["Strategy"] = "ESA"
    strategy_data["ESA"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["ESA"]["Trade_PNL"] = 0
    strategy_data["ESA"]["Todays_PNL"] = 0

    strategy_data["SN"] = {}
    strategy_data["SN"]["Strategy"] = "SN"
    strategy_data["SN"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["SN"]["Trade_PNL"] = 0
    strategy_data["SN"]["Todays_PNL"] = 0

    strategy_data["Weekly_MR"] = {}
    strategy_data["Weekly_MR"]["Strategy"] = "Weekly_MR"
    strategy_data["Weekly_MR"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["Weekly_MR"]["Trade_PNL"] = 0
    strategy_data["Weekly_MR"]["Todays_PNL"] = 0

    strategy_data["DailyMR"] = {}
    strategy_data["DailyMR"]["Strategy"] = "DailyMR"
    strategy_data["DailyMR"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["DailyMR"]["Trade_PNL"] = 0
    strategy_data["DailyMR"]["Todays_PNL"] = 0

    strategy_data["90D_Volatility"] = {}
    strategy_data["90D_Volatility"]["Strategy"] = "90D_Volatility"
    strategy_data["90D_Volatility"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["90D_Volatility"]["Trade_PNL"] = 0
    strategy_data["90D_Volatility"]["Todays_PNL"] = 0

    strategy_data["M12-M1"] = {}
    strategy_data["M12-M1"]["Strategy"] = "M12-M1"
    strategy_data["M12-M1"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["M12-M1"]["Trade_PNL"] = 0
    strategy_data["M12-M1"]["Todays_PNL"] = 0

    strategy_data["SML"] = {}
    strategy_data["SML"]["Strategy"] = "SML"
    strategy_data["SML"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["SML"]["Trade_PNL"] = 0
    strategy_data["SML"]["Todays_PNL"] = 0

    strategy_data["Stock_Momentum"] = {}
    strategy_data["Stock_Momentum"]["Strategy"] = "Stock_Momentum"
    strategy_data["Stock_Momentum"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["Stock_Momentum"]["Trade_PNL"] = 0
    strategy_data["Stock_Momentum"]["Todays_PNL"] = 0
    strategy_data["Stock_Momentum"]["Nifty_hedge"] = 0



