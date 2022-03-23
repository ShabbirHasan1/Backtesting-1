import datetime

import numpy as np
import pandas as pd
from Individual_Trades import Individual_Trades
from my_funcs import *
import warnings

def combined_portfolio_pnl_generation(universal_dates,expiry_days,baseamount,exposure_limit,strategy_details,price_data,
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
    strategy_data["RSI"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["RSC"] = {}
    strategy_data["RSC"]["Strategy"] = "RSC"
    strategy_data["RSC"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["RSC"]["Trade_PNL"] = 0
    strategy_data["RSC"]["Todays_PNL"] = 0
    strategy_data["RSC"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["ESA"] = {}
    strategy_data["ESA"]["Strategy"] = "ESA"
    strategy_data["ESA"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["ESA"]["Trade_PNL"] = 0
    strategy_data["ESA"]["Todays_PNL"] = 0
    strategy_data["ESA"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["SN"] = {}
    strategy_data["SN"]["Strategy"] = "SN"
    strategy_data["SN"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["SN"]["Trade_PNL"] = 0
    strategy_data["SN"]["Todays_PNL"] = 0
    strategy_data["SN"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["Weekly_MR"] = {}
    strategy_data["Weekly_MR"]["Strategy"] = "Weekly_MR"
    strategy_data["Weekly_MR"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["Weekly_MR"]["Trade_PNL"] = 0
    strategy_data["Weekly_MR"]["Todays_PNL"] = 0
    strategy_data["Weekly_MR"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)


    strategy_data["DailyMR"] = {}
    strategy_data["DailyMR"]["Strategy"] = "DailyMR"
    strategy_data["DailyMR"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["DailyMR"]["Trade_PNL"] = 0
    strategy_data["DailyMR"]["Todays_PNL"] = 0
    strategy_data["DailyMR"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)


    strategy_data["90D_Volatility"] = {}
    strategy_data["90D_Volatility"]["Strategy"] = "90D_Volatility"
    strategy_data["90D_Volatility"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["90D_Volatility"]["Trade_PNL"] = 0
    strategy_data["90D_Volatility"]["Todays_PNL"] = 0
    strategy_data["90D_Volatility"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["M12-M1"] = {}
    strategy_data["M12-M1"]["Strategy"] = "M12-M1"
    strategy_data["M12-M1"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["M12-M1"]["Trade_PNL"] = 0
    strategy_data["M12-M1"]["Todays_PNL"] = 0
    strategy_data["M12-M1"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["SML"] = {}
    strategy_data["SML"]["Strategy"] = "SML"
    strategy_data["SML"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["SML"]["Trade_PNL"] = 0
    strategy_data["SML"]["Todays_PNL"] = 0
    strategy_data["SML"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    strategy_data["Stock_Momentum"] = {}
    strategy_data["Stock_Momentum"]["Strategy"] = "Stock_Momentum"
    strategy_data["Stock_Momentum"]["Positions"] = pd.DataFrame(0,
        columns=["QTY", "Side", "Entry_price", "Todays_price", "Yesterdays_price", "Todays_PNL", "Trade_PNL"])
    strategy_data["Stock_Momentum"]["Trade_PNL"] = 0
    strategy_data["Stock_Momentum"]["Todays_PNL"] = 0
    strategy_data["Stock_Momentum"]["Nifty_hedge"] = 0
    strategy_data["Stock_Momentum"]["Daily_exposure_data"]=pd.DataFrame(0,columns=universal_dates,index=symbols)

    pnl_series=pd.DataFrame(0,columns=symbols,index=universal_dates)
    current_position_history=pd.DataFrame(0,columns=symbols,index=universal_dates)
    current_position_exposure=pd.DataFrame(0,columns=symbols,index=universal_dates)
    current_position_perc_history=pd.DataFrame(0,columns=symbols,index=universal_dates)
    current_pnl_history=pd.DataFrame(0,columns=symbols,index=universal_dates)
    adjustment_positions_history=pd.DataFrame(0,columns=symbols,index=universal_dates)
    adjustment_positions_history_perc=pd.DataFrame(0,columns=symbols,index=universal_dates)

    portfolio_values=pd.DataFrame(0,columns=["PNL","net_exposure","gross_exposure","AUM","PNL_percentage"],index=universal_dates)
    price_data_close_series=pd.DataFrame(0,index=universal_dates,columns=symbols_data_list)
    price_data_close_next_series = pd.DataFrame(0, index=universal_dates, columns=symbols_data_list)

    month_end_AUM=pd.DataFrame(0,columns=strategy_list,index=monthly_index)
    month_end_AUM["Total"]=0

    current_positions=pd.DataFrame(0,columns=["Position","Close_price","Exposure","Exposrue_in_perc","Gross_exposure_in_perc"],index=symbols)
    adjustment_positions=pd.DataFrame(0,columns=["Position","Close_price","Percentage"],index=symbols)
    strategy_position=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_exposure=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_exposure_in_perc=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_pnl=pd.DataFrame(0,columns=strategy_details.index,index=symbols)

    strategy_gross_exposure=pd.DataFrame(0,columns=strategy_details.index,index=universal_dates)
    strategy_net_exposure=pd.DataFrame(0,columns=strategy_details.index,index=universal_dates)
    strategy_net_PNL=pd.DataFrame(0,columns=strategy_details.index,index=universal_dates)
    strategy_net_PNL_perc=pd.DataFrame(0,columns=strategy_details.index,index=universal_dates)

    final_trade_register=pd.DataFrame(columns=individual_trade_list.columns)

    for contract in symbols_data_list:
        price_data_close_series[contract]=price_data[contract]["Close"]
        price_data_close_next_series[contract]=futures_2_data[contract]["Close"]

    price_data_close_series.ffill(inplace=True)
    price_data_close_series.fillna(0,inplace=True)


    price_data_close_next_series.ffill(inplace=True)
    price_data_close_next_series.fillna(0,inplace=True)

    month_end_closing_prices=price_data_close_series.resample("M").last()
    expiry_days_next_series_closing_prices=price_data_close_next_series.loc[expiry_days]

    month_end_qty = 1000000/month_end_closing_prices

    if Individual_Trades.trade_register!=[]:
        Individual_Trades.trade_register[0].re_initialise()
    start_of_month_Total_AUM=baseamount

    previous_day=universal_dates[0]

    print("PNL calculation started")

    for current_month in monthly_index:
        if current_month==monthly_index[0]:
            current_month_momentum_qty=(0.035*strategy_details.loc["Stock_Momentum","Weightage"]*
                                        start_of_month_Total_AUM/10000000*(month_end_qty.loc[current_month]))

        else:
            current_month_momentum_qty = (0.035 * strategy_details.loc["Stock_Momentum", "Weightage"] *
                                          start_of_month_Total_AUM / 10000000 * (month_end_qty.shift().loc[current_month]))

        current_month_dates=universal_dates[(universal_dates.month==current_month.month) &
        (universal_dates.year==current_month.year)]

        current_month_trades=individual_trade_list[individual_trade_list["Date"].map(
            lambda x:(x.year==current_month.year) &(x.month==current_month.month))]

        last_day_of_month=current_month_dates[-1]
        expiry_day_of_month=[expiry for expiry in expiry_days if expiry in current_month_dates][0]

        print(f"\n Processing: {current_month.month}--{current_month.year}")

        for current_day in current_month_dates:
            todays_trade.drop(todays_trade.index,inplace=True)


            ###update PNL in yesterdays positions:

            todays_close_price=price_data_close_series.loc[current_day]
            todays_nifty_price=todays_close_price["Nz1 Index"]
            if previous_day!=expiry_day_of_month:
                yesterdays_close_price=price_data_close_series.shift().loc[current_day]
            else:
                yesterdays_close_price=price_data_close_next_series.shift().loc[current_day]

            current_positions["Close_price"]=todays_close_price
            current_positions["Previous_close_price"]=yesterdays_close_price
            current_positions["Todays_position_PNL"]=current_positions["Positions"]*(
                    current_positions["Close_price"]-current_positions["Previous_close_price"])

            portfolio_values.loc[current_day,"PNL"]=current_positions["Todays_position_PNL"].sum()
            portfolio_values.loc[current_day,"PNL_percentage"]=portfolio_values.loc[current_day,"PNL"]/previous_day_AUM
            portfolio_values.loc[current_day, "AUM"] = portfolio_values.loc[
                                                                      current_day, "PNL"] + previous_day_AUM

            if current_day==current_month_dates[0]:
                strategy_details["Current_AUM"]=start_of_month_Total_AUM*strategy_details["Weightage"]

            for strategy in strategy_list:

                strategy_exposure[strategy]=strategy_position[strategy]*todays_close_price
                strategy_pnl[strategy]=strategy_position[strategy]*(todays_close_price-yesterdays_close_price)
                strategy_net_PNL.locp[current_day,strategy]=strategy_pnl[strategy].sum()
                strategy_net_PNL_perc.loc[current_day,strategy]=strategy_pnl[strategy].sum()/(strategy_details.loc[strategy,"Current_AUM"])

                if not strategy_data[strategy]["Positions"].empty:
                    strategy_data[strategy]["Positions"]["Todays_price"]=todays_close_price
                    strategy_data[strategy]["Positions"]["Yesterdays_price"] = yesterdays_close_price
                    strategy_data[strategy]["Positions"]["Todays_PNL"]=((strategy_data[strategy]["Positions"]["Todays_price"]/
                                                                        strategy_data[strategy]["Positions"]["Yesterdays_price"])-1
                                                                        )*strategy_data[strategy]["Positions"]["Side"]
                    strategy_data[strategy]["Positions"]["Trade_PNL"]=((strategy_data[strategy]["Positions"]["Todays_price"]/
                                                                        strategy_data[strategy]["Positions"]["Entry_price"])-1
                                                                        )*strategy_data[strategy]["Positions"]["Side"]
                    strategy_data[strategy]["Trade_PNL"]=strategy_data[strategy]["Positions"]["Trade_PNL"].mean()
                    strategy_data[strategy]["Todays_PNL"]=strategy_data[strategy]["Positions"]["Todays_PNL"].mean()

            ### update PNL for yesterdays positions block closed

            for strategy in strategy_list:

                todays_strategy_trades=current_month_trades[(current_month_trades["Date"]==current_day) &(current_month_trades["Strategy"]==Strategy)]
                todays_strategy_trades.reset_index(inplace=True,drop=True)
                strategy_exit_trades.drop(strategy_exit_trades.index,inplace=True)

                if strategy=="Stock_Momentum":
                    todays_strategy_trades["Qty"]=todays_strategy_trades["Qty"]*(todays_strategy_trades["Contract"].map(current_month_momentum_qty))
                    todays_trade=todays_trade.append(pd.concat([todays_strategy_trades]))
                    todays_trade.reset_index(inplace=True,drop=True)

                    strategy_position[strategy]=update_positions(todays_strategy_trades,strategy_position[strategy])

                else:
                    strategy_per_trade_value=strategy_details.loc[strategy,"Current_AUM"]/(strategy_details.loc[strategy,"Stocks"])
                    todays_strategy_trades["Qty"]=strategy_per_trade_value/todays_strategy_trades["Price"]

                    if to


