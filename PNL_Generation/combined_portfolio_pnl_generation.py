import pandas as pd
import numpy as np
import openpyxl as xl
import datetime
from pathlib import Path
import collections

from Individual_Trades import Individual_Trades
from Trade_Generation import creating_individual_trade,creating_individual_trade_db
from Timeframe_Manipulation import series_resampling as tm
from PNL_Generation import  pnl_generation as pg
from my_funcs import *

import warnings

def update_positions(trade_list,current_holdings):
    for i, trade in trade_list.iterrows():
        current_holdings.loc[trade["Contract"]]+=trade["Qty"]*trade["Side"]

    return current_holdings

def set_dataframe(df):
    df.columns=df.loc[0]
    df.drop(0,inplace=True)
    df.set_index("Dates",inplace=True)

def saving_dataframes(portfolio_values,name,output_folder):

    portfolio_values.name=name
    to_be_saved_as_csv=[portfolio_values]
    excel_creation(to_be_saved_as_csv,output_folder,name)

def create_trade_line(trades_list,account,strategy_a,date,price_list):
    trade_table=pd.DataFrame(columns=["Account","Strategy","Date", "Price", "Side", "Contract", "Underlying","Contract_Type", "Qty", "Trading_Cost", "Strike_Price"])
    trades_list=trades_list.groupby(trades_list.index).sum()
    price_list=price_list.groupby(price_list.index).first()
    for stock in trades_list.index:
        Account=account
        Strategy=strategy_a
        Date=date
        Price=price_list[stock]
        Side=np.sign(trades_list[stock])
        Contract=stock
        Underlying=stock
        Contract_Type="F"
        Qty=abs(trades_list[stock])
        Trading_Cost=0
        Strike_Price=0
        new_trade_line=[Account,Strategy,Date, Price, Side, Contract, Underlying,Contract_Type, Qty, Trading_Cost, Strike_Price]
        trade_table.loc[len(trade_table)]=new_trade_line

    return trade_table

def check_for_exposure(current_positions,adjustment_positions,todays_position,previous_day_AUM):
    todays_adjustment_positions=pd.Series()
    current_adjustment_positions=adjustment_positions[adjustment_positions["Position"]!=0]

    for stock in current_adjustment_positions.index:
        if stock in todays_position.index:
            if (np.sign(todays_position[stock]))==(np.sign(current_adjustment_positions.loc[stock,"Position"])):
                adjustment_positions.loc[stock,"Position"]+=todays_position[stock]
            elif abs(current_adjustment_positions.loc[stock,"Position"])>=abs(todays_position[stock]):
                adjustment_positions.loc[stock,"Position"]+=todays_position[stock]
            else:
                todays_position[stock]+=current_adjustment_positions.loc[stock,"Position"]
                todays_adjustment_positions[stock]=todays_position[stock]
                adjustment_positions.loc[stock, "Position"]=0

    current_positions["Position"]=current_positions["Position"].add(todays_position,fill_value=0)
    current_positions["Exposure"]=current_positions["Close_price"]*current_positions["Position"]
    current_positions["Exposure_in_perc"]=current_positions["Exposure"]/previous_day_AUM
    current_positions["Gross_exposure_in_perc"]=current_positions["Exposure_in_perc"].abs()

    return current_positions,adjustment_positions,todays_adjustment_positions



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
    underlying=individual_trade_list["Underlying"].unique()
    symbols_1=pd.Series(symbols)

    individual_trade_list.sort_values(by=["Date","Contract"],ignore_index=True,inplace=True)
    individual_trade_list["Qty"]=individual_trade_list["Qty"].astype(float)
    individual_trade_list["Side"]=individual_trade_list["Side"].astype(float)

    symbols_data_list=pd.Series(price_data.keys())
    todays_trade=pd.DataFrame(columns=individual_trade_list.columns)
    strategy_exit_trades=pd.DataFrame(columns=individual_trade_list.columns)

    #checking if any symbol data is missing
    symbols_data_unavailable=symbols_1[~symbols_1.isin(symbols_data_list)]

    if ~pd.isnull(symbols_data_unavailable).asll():
        print(f"Following symbols data not fount \n"
              f"{symbols_data_unavailable[symbols_data_unavailable.notnull()]}")
        quit()
    else:
        print("========ALL DATA FOUND========")
    check_status=0
    strategy_data={}

    strategy_data["RSI"]={}
    strategy_data["RSI"]["Strategy"]="RSI"
    strategy_data["RSI"]["Positions"]=pd.DataFrame(columns=
                                                   ["Qty","Side","Entry_price","Todays_Price","Yesterdays_price","Todays_PNL","Trade_PNL"])
    strategy_data["RSC"]["Trade_PNL"]=0
    strategy_data["RSC"]["Todays_PNL"]=0

    strategy_data["RSC"] = {}
    strategy_data["RSC"]["Strategy"] = "RSI"
    strategy_data["RSC"]["Positions"] = pd.DataFrame(columns=
                                                     ["Qty", "Side", "Entry_price", "Todays_Price", "Yesterdays_price",
                                                      "Todays_PNL", "Trade_PNL"])
    strategy_data["ESA"]["Trade_PNL"] = 0
    strategy_data["ESA"]["Todays_PNL"] = 0

    strategy_data["ESA"] = {}
    strategy_data["ESA"]["Strategy"] = "RSI"
    strategy_data["ESA"]["Positions"] = pd.DataFrame(columns=
                                                     ["Qty", "Side", "Entry_price", "Todays_Price", "Yesterdays_price",
                                                      "Todays_PNL", "Trade_PNL"])
    strategy_data["ESA"]["Trade_PNL"] = 0
    strategy_data["ESA"]["Todays_PNL"] = 0

    strategy_data["SN"] = {}
    strategy_data["SN"]["Strategy"] = "RSI"
    strategy_data["SN"]["Positions"] = pd.DataFrame(columns=
                                                     ["Qty", "Side", "Entry_price", "Todays_Price", "Yesterdays_price",
                                                      "Todays_PNL", "Trade_PNL"])
    strategy_data["SN"]["Trade_PNL"] = 0
    strategy_data["SN"]["Todays_PNL"] = 0

    strategy_data["Weekly_MR"] = {}
    strategy_data["Weekly_MR"]["Strategy"] = "RSI"
    strategy_data["Weekly_MR"]["Positions"] = pd.DataFrame(columns=
                                                     ["Qty", "Side", "Entry_price", "Todays_Price", "Yesterdays_price",
                                                      "Todays_PNL", "Trade_PNL"])
    strategy_data["Weekly_MR"]["Trade_PNL"] = 0
    strategy_data["Weekly_MR"]["Todays_PNL"] = 0

    strategy_data["DailyMR"] = {}
    strategy_data["DailyMR"]["Strategy"] = "RSI"
    strategy_data["DailyMR"]["Positions"] = pd.DataFrame(columns=
                                                           ["Qty", "Side", "Entry_price", "Todays_Price",
                                                            "Yesterdays_price",
                                                            "Todays_PNL", "Trade_PNL"])
    strategy_data["DailyMR"]["Trade_PNL"] = 0
    strategy_data["DailyMR"]["Todays_PNL"] = 0

    strategy_data["Stock_Momentum"] = {}
    strategy_data["Stock_Momentum"]["Strategy"] = "RSI"
    strategy_data["Stock_Momentum"]["Positions"] = pd.DataFrame(columns=
                                                           ["Qty", "Side", "Entry_price", "Todays_Price",
                                                            "Yesterdays_price",
                                                            "Todays_PNL", "Trade_PNL"])
    strategy_data["Stock_Momentum"]["Trade_PNL"] = 0
    strategy_data["Stock_Momentum"]["Todays_PNL"] = 0

    strategy_data["90D_Volatility"] = {}
    strategy_data["90D_Volatility"]["Strategy"] = "RSI"
    strategy_data["90D_Volatility"]["Positions"] = pd.DataFrame(columns=
                                                                ["Qty", "Side", "Entry_price", "Todays_Price",
                                                                 "Yesterdays_price",
                                                                 "Todays_PNL", "Trade_PNL"])
    strategy_data["90D_Volatility"]["Trade_PNL"] = 0
    strategy_data["90D_Volatility"]["Todays_PNL"] = 0

    strategy_data["M12-M1"] = {}
    strategy_data["M12-M1"]["Strategy"] = "RSI"
    strategy_data["M12-M1"]["Positions"] = pd.DataFrame(columns=
                                                                ["Qty", "Side", "Entry_price", "Todays_Price",
                                                                 "Yesterdays_price",
                                                                 "Todays_PNL", "Trade_PNL"])
    strategy_data["M12-M1"]["Trade_PNL"] = 0
    strategy_data["M12-M1"]["Todays_PNL"] = 0

    strategy_data["SML"] = {}
    strategy_data["SML"]["Strategy"] = "RSI"
    strategy_data["SML"]["Positions"] = pd.DataFrame(columns=
                                                                ["Qty", "Side", "Entry_price", "Todays_Price",
                                                                 "Yesterdays_price",
                                                                 "Todays_PNL", "Trade_PNL"])
    strategy_data["SML"]["Trade_PNL"] = 0
    strategy_data["SML"]["Todays_PNL"] = 0

    current_position_history=pd.DataFrame(columns=symbols,index=universal_dates)
    current_position_exposure=pd.DataFrame(columns=symbols,index=universal_dates)
    current_position_perc_history=pd.DataFrame(columns=symbols,index=universal_dates)
    adjustments_position_history=pd.DataFrame(columns=symbols,index=universal_dates)
    adjustments_position_history_perc=pd.DataFrame(columns=symbols,index=universal_dates)
    price_data_close_series=pd.DataFrame(0,columns=symbols,index=universal_dates)
    price_data_close_next_series=pd.DataFrame(0,columns=symbols,index=universal_dates)
    daily_exposure=pd.DataFrame(columns=symbols,index=universal_dates)
    weekly_exposure=pd.DataFrame(columns=symbols,index=universal_dates)
    sn_exposure=pd.DataFrame(columns=symbols,index=universal_dates)
    ESA_exposure = pd.DataFrame(columns=symbols, index=universal_dates)
    stock_momentum_exposure = pd.DataFrame(columns=symbols, index=universal_dates)
    rsi_exposure = pd.DataFrame(columns=symbols, index=universal_dates)
    rsc_exposure = pd.DataFrame(columns=symbols, index=universal_dates)
    d90_vol_exposure = pd.DataFrame(columns=symbols, index=universal_dates)
    M12_M1_ret_exposure = pd.DataFrame(columns=symbols, index=universal_dates)
    SML_ret_exposure=pd.DataFrame(columns=symbols,index=universal_dates)


    portfolio_values=pd.DataFrame(columns=["PNL","net_exposure","gross_exposure","AUM","PNL_percentage"],
                                  index=universal_dates)

    month_end_AUM=pd.DataFrame(0,columns=[strategy_list,"Total"],index=monthly_index)

    current_positions=pd.DataFrame(0,columns=["Position","Close_price","Exposure","Exposure_in_perc","Gross_exposure_in_perc"],
    index=symbols)

    adjustment_positions=pd.DataFrame(0,columns=["Position","Close_price","Percentage"],index=symbols)
    strategy_position=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_exposure=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_exposure_in_perc=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_pnl=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_gross_exposure=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_net_exposure=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_net_PNL=pd.DataFrame(0,columns=strategy_details.index,index=symbols)
    strategy_net_PNL_perc=pd.DataFrame(0,columns=strategy_details.index,index=symbols)

    final_trade_register=pd.DataFrame(columns=individual_trade_list.columns)

    for contract in symbols:
        price_data_close_series=price_data[contract]["Close"]
        price_data_close_next_series=futures_2_data[contract]["Close"]

    price_data_close_series.ffill(inplace=True)
    price_data_close_series.fillna(0,inplace=True)

    price_data_close_next_series.ffill(inplace=True)
    price_data_close_next_series.fillna(0,inplace=True)

    month_end_closing_prices=price_data_close_series.resample("M").last()
    expiry_days_next_series_closing_prices=price_data_close_next_series.loc[expiry_days]

    month_end_qty=1000000/month_end_closing_prices

    if Individual_Trades.trade_register!=[]:
        Individual_Trades.trade_register[0].re_initialise()
    start_of_month_Total_AUM=baseamount

    previous_day=universal_dates[0]

    print("PNL calculation started")

    for current_month in monthly_index:
        if current_month==monthly_index[0]:
            current_month_momentum_qty=(0.035*strategy_details.loc["Stock_momentum","Weightage"]*start_of_month_Total_AUM/1000000)*(month_end_qty.loc[current_month])
        else:
            current_month_momentum_qty = (0.035 * strategy_details.loc[
                "Stock_momentum", "Weightage"] * start_of_month_Total_AUM / 1000000) *(month_end_qty.shift().loc[current_month])

        current_month_dates=universal_dates[(universal_dates.month==current_month.month)&(universal_dates.year==current_month.year)]
        current_month_trades=individual_trade_list[individual_trade_list["Date"].map(
            lambda x: (x in current_month_dates) )]

        last_day_of_month=current_month_dates[-1]
        expiry_day_for_month=[expiry for expiry in expiry_days if expiry in current_month_trades][0]

        print(f"\n Processing: {current_month.month}--{current_month.year}")

        for current_day in current_month_dates:
            todays_trade.drop(todays_trade.index,inplace=True)

            if current_day==datetime.datetime(2012,1,1):
                print(f"\n processing : {current_day}")


            ### Update PNL for yesterdays positions

            todays_close_price=price_data_close_series[current_day]
            todays_nifty_price=todays_close_price["Nz1 Index"]
            if previous_day!=expiry_day_for_month:
                yesterdays_close_price=price_data_close_series.shift().loc[current_day]
            else:
                yesterdays_close_price = price_data_close_next_series.shift().loc[current_day]

            current_positions["Close_price"]=todays_close_price
            current_positions["Previous_Close_price"]=yesterdays_close_price
            current_positions["Todays_position_PNL"]=current_positions["Position"]*\
                                                     (current_positions["Close_price"]-current_positions["Previous_Close_price"])

            portfolio_values.loc[current_day,"PNL"]=current_positions["Todays_position_PNL"].sum()
            portfolio_values.loc[current_day,"PNL_percentage"]=portfolio_values.loc[current_day,"PNL"]/previous_day_AUM
            portfolio_values.loc[current_day,"AUM"]=previous_day_AUM+portfolio_values.loc[current_day,"PNL"]

            if current_day==current_month_dates[0]:
                strategy_details["Current_AUM"]=start_of_month_Total_AUM*strategy_details["Weightage"]

            for strategy in strategy_list:
                strategy_exposure[strategy]=strategy_position[strategy]*todays_close_price
                strategy_pnl[strategy]=strategy_position[strategy]*(todays_close_price-yesterdays_close_price)
                strategy_net_PNL.loc[current_day,strategy]=strategy_pnl[strategy].sum()
                strategy_net_PNL_perc.loc[current_day, strategy] = strategy_pnl[strategy].sum() / \
                                                                   (strategy_details.loc[strategy,"Current_AUM"])

                if not strategy_data[strategy]["Positions"].empty:
                    strategy_data[strategy]["Positions"]["Todays_price"]=todays_close_price
                    strategy_data[strategy]["Positions"]["Yesterdays_price"]=yesterdays_close_price
                    strategy_data[strategy]["Positions"]["Todays_PNL"]=((strategy_data[strategy]["Positions"]["Todays_price"])/
                                                                        (strategy_data[strategy]["Positions"]["Yesterdays_price"])-1) \
                                                                       * (strategy_data[strategy]["Positions"]["Side"])
                    strategy_data[strategy]["Positions"]["Trade_PNL"]=((strategy_data[strategy]["Positions"]["Todays_price"])/
                                                                        (strategy_data[strategy]["Positions"]["Entry_price"])-1) \
                                                                       * (strategy_data[strategy]["Positions"]["Side"])
                    strategy_data[strategy]["Trade_PNL"]=strategy_data[strategy]["Positions"]["Trade_PNL"].mean()
                    strategy_data[strategy]["Trade_PNL"]=strategy_data[strategy]["Positions"]["Todays_PNL"].mean()

            ### update PNL for yesterdays positions block closed

            for strategy in strategy_list:
                todays_strategy_trades=current_month_trades[(current_month_trades["Date"]==current_day) &(current_month_trades["Strategy"]==strategy)]
                todays_strategy_trades.reset_index(inplace=True,drop=True)
                strategy_exit_trades.drop(strategy_exit_trades.index,inplace=True)

                if strategy=="Stock_Momentum":
                    todays_strategy_trades["Qty"]=todays_strategy_trades["Qty"]*(todays_strategy_trades["Contract"].map(current_month_momentum_qty))
                    todays_trade=todays_trade.append(pd.concat([todays_strategy_trades]))
                    todays_trade.reset_index(inplace=True, drop=True)
                    strategy_position[strategy]=update_positions(todays_strategy_trades,strategy_position[strategy])

                else:
                    strategy_per_trade_value=strategy_details.loc[strategy,"Current_AUM"]/(strategy_details.loc[strategy,"Stocks"])
                    todays_strategy_trades["Qty"]=strategy_per_trade_value/todays_strategy_trades["Price"]

                    if todays_strategy_trades.empty:
                        ##check strategy PNL for stop loss block starts here
                        if strategy in ["RSI","RSC","SN","ESA","90D_volatility","SML","M12-M1"]:
                            if (strategy_data[strategy]["Trade_PNL"]<(strategy_details.loc[strategy,"Stop_Loss"]*0.5)):
                                strategy_data[strategy]["Positions"].drop(strategy_data[strategy]["Positions"].index,inplace=True)

                                strategy_data[strategy]["Trade_PNL"]=0
                                strategy_data[strategy]["Todays_PNL"]=0

                                current_strategy_positions=strategy_position[strategy]
                                current_strategy_positions=current_strategy_positions[current_strategy_positions!=0]
                                strategy_exit_trades=create_trade_line(current_strategy_positions*-1,"",strategy,current_day,todays_close_price)
                                strategy_position[strategy]=update_positions(strategy_exit_trades,strategy_position[strategy])

                        ##check strategy PNL for stop loss block ends here
                    else:
                        if not strategy_data[strategy]["Positions"].empty:
                            current_strategy_positions=strategy_position[strategy]
                            current_strategy_positions=current_strategy_positions[current_strategy_positions!=0]
                            strategy_exit_trades=create_trade_line(current_strategy_positions*-1,"",strategy,current_day,todays_close_price)
                            strategy_position[strategy]=update_positions(strategy_exit_trades,strategy_position[strategy])

                        temp_todays_strategy_trade=todays_strategy_trades.copy()
                        temp_todays_strategy_trade.set_index(temp_todays_strategy_trade["Contract"],inplace=True,drop=True)
                        strategy_data[strategy]["Positions"].drop(strategy_data[strategy]["Positions"].index,inplace=True)
                        strategy_data[strategy]["Positions"].reindex(temp_todays_strategy_trade["Contract"])
                        strategy_data[strategy]["Positions"]["Qty"]=temp_todays_strategy_trade["Qty"]
                        strategy_data[strategy]["Positions"]["Side"]=temp_todays_strategy_trade["Side"]
                        strategy_data[strategy]["Positions"]["Entry_price"]=temp_todays_strategy_trade["Price"]

                    todays_trade=todays_trade.append(pd.concat([todays_strategy_trades,strategy_exit_trades]))
                    todays_trade.reset_index(inplace=True,drop=True)
                    strategy_position[strategy]=update_positions(todays_strategy_trades,strategy_position[strategy])


                strategy_exposure[strategy]=strategy_position[strategy]*todays_close_price
                strategy_exposure_in_perc[strategy]=strategy_exposure[strategy]/(strategy_details.loc[strategy,"Current_AUM"])
                strategy_net_exposure.loc[current_day,strategy]=(strategy_exposure[strategy].sum())/(strategy_details.loc[strategy,"Current_AUM"])
                strategy_gross_exposure.loc[current_day, strategy] = (strategy_exposure[strategy].abs().sum()) / (
                strategy_details.loc[strategy, "Current_AUM"])

            if current_day==last_day_of_month:
                previou_month_aum=start_of_month_Total_AUM
                start_of_month_Total_AUM=portfolio_values.loc[current_day,"PNL"]+previous_day_AUM

                for strategy in strategy_list:
                    strategy_details.loc[strategy,"Current_AUM"]=start_of_month_Total_AUM*strategy_details.loc[strategy,"Weightage"]
                    current_month_strategy_positions=strategy_position[strategy]
                    current_month_strategy_positions=current_month_strategy_positions[current_month_strategy_positions.abs()>1]
                    next_month_strategy_price=todays_close_price[current_month_strategy_positions.index]
                    if strategy=="Stock_Momentum":
                        per_stock_value=(strategy_details.loc[strategy,"Current_AUM"]*0.035)
                        current_month_momentum_qty=current_month_strategy_positions.abs()/current_month_momentum_qty
                        current_month_momentum_qty=current_month_momentum_qty[next_month_strategy_price.index]
                        next_month_positions=per_stock_value/next_month_strategy_price
                        next_month_positions=np.sign(current_month_strategy_positions)*next_month_positions
                        month_end_trade_required=next_month_positions-current_month_strategy_positions
                        if "Nz1 Index" in month_end_trade_required.index:
                            month_end_trade_required.drop("Nz1 Index", inplace=True)

                    else:
                        adjustment_factor=(start_of_month_Total_AUM/previou_month_aum)
                        next_month_positions=current_month_strategy_positions*adjustment_factor
                        month_end_trade_required=next_month_positions=current_month_strategy_positions

                    trade_list=create_trade_line(month_end_trade_required,"",strategy,current_day,todays_close_price)
                    strategy_position[strategy]=update_positions(trade_list,strategy_position[strategy])

                    todays_trade=pd.concat([todays_trade,trade_list],axis=0)

                    strategy_exposure[strategy]=strategy_position[strategy]*todays_close_price
                    strategy_exposure_in_perc[strategy]=strategy_exposure[strategy]/((start_of_month_Total_AUM*strategy_details.loc[strategy,"Weightage"]))
                    strategy_net_exposure.loc[current_day,strategy]=(strategy_exposure[strategy].sum())/(strategy_details.loc[strategy,"Current_AUM"])
                    strategy_gross_exposure.loc[current_day,strategy]=(strategy_exposure[strategy].abs().sum())/(strategy_details.loc[strategy,"Current_AUM"])


            #creating trade lines for stock Momentum hedge with nifty

            strategy_exposure["Stock_Momentum"]=strategy_position["Stock_Momentum"]*todays_close_price
            strategy_exposure_in_perc["Stock_Momentum"]=strategy_exposure["Stock_Momentum"]/(start_of_month_Total_AUM*strategy_details.loc["Stock_Momentum","Weightage"])
            net_stock_exposure_stock_momentum=strategy_exposure["Stock_Momentum"].sum()-strategy_exposure.loc["Nz1 Index","Stock_momentum"]
            stock_momentum_hedge_required=-1*(net_stock_exposure_stock_momentum)/todays_close_price["Nz1 Index"]

            todays_nifty_hedge_trade=stock_momentum_hedge_required-current_stock_momentum_hedge
            current_stock_momentum_hedge=stock_momentum_hedge_required
            strategy_position.loc["Nz1 Index","Stock_Momentum"]=stock_momentum_hedge_required

            strategy_exposure["Stock_Momentum"]=strategy_position["Stock_Momentum"]*todays_close_price
            strategy_exposure_in_perc["Stock_Momentum"]=strategy_exposure["Stock_Momentum"]/(start_of_month_Total_AUM*strategy_details.loc["Stock_Momentum","Weightage"])
            strategy_net_exposure.loc[current_day, "Stock_Momentum"] = (strategy_exposure["Stock_Momentum"].sum()) / (previous_day_AUM*strategy_details.loc["Stock_Momentum", "Weightage"])
            strategy_gross_exposure.loc[current_day, "Stock_Momentum"] = (strategy_exposure["Stock_Momentum"].abs().sum()) / (previous_day_AUM*strategy_details.loc["Stock_Momentum", "Weightage"])

            new_trade_line=["Nifty Hedge","Stock_Momentum",current_day,todays_nifty_price,np.sign(todays_nifty_hedge_trade),"Nz1 Index","Nz1 Index",
                            "F",abs(todays_nifty_hedge_trade),0,0]

            todays_trade.reset_index(inplace=True,drop=True)
            todays_trade.loc[len(todays_trade.index)]=new_trade_line
            # block for nifty hedge calculation ends here

            daily_exposure[current_day]=strategy_position["DailyMR"]
            weekly_exposure[current_day]=strategy_position["Weekly_MR"]
            sn_exposure[current_day]=strategy_position["SN"]
            ESA_exposure[current_day]=strategy_position["ESA"]
            stock_momentum_exposure[current_day]=strategy_position["Stock_Momentum"]
            rsi_exposure[current_day]=strategy_position["RSI"]
            rsc_exposure[current_day]=strategy_position["RSC"]
            d90_vol_exposure[current_day]=strategy_position["90D_Volatility"]
            M12_M1_ret_exposure[current_day]=strategy_position["M12-M1"]
            SML_ret_exposure[current_day]=strategy_position["SML"]

            net_trades=todays_trade[["Contract","Qty","Side"]]
            net_trades["Positions"]=net_trades["Qty"]*net_trades["Side"]
            net_trades=net_trades.groupby("Contract").sum(["Positions"])

            todays_position=net_trades["Positions"]
            current_positions["Close_price"]=todays_close_price

            current_positions,adjustment_positions,position_adjustment_trades=check_for_exposure(current_positions,adjustment_positions,todays_position,previous_day_AUM)

            if len(position_adjustment_trades.index)!=0:
                trade_list=create_trade_line(position_adjustment_trades,"","Adjustment_trades",current_day,todays_close_price)
                todays_trade=pd.concat([todays_trade,trade_list],axis=0)

            positions_exceeded=current_positions[current_positions["Gross_exposure_in_perc"]>exposure_limit]
            if "Nz1 Index" in positions_exceeded.index:
                positions_exceeded=positions_exceeded.drop("Nz1 index")

            if len(positions_exceeded)!=0:

#                new_adjustment_trades=create_trade_line(positions_exceeded,"","Adjustment_trades",current_day,todays_close_price)
#                todays_trade=pd.concat([todays_trade,new_adjustment_trades],axis=0)

                for exceeded_position_stock in positions_exceeded.index:

                    exceeded_amount_in_perc=positions_exceeded.loc[exceeded_position_stock]["Gross_exposure_in_perc"]-exposure_limit
                    exceeded_amount_in_amount=exceeded_amount_in_perc*previous_day_AUM
                    Account=""
                    Strategy="Adjustment_trades"
                    Date=current_day
                    Price=todays_close_price[exceeded_position_stock]
                    Side=1 if positions_exceeded.loc[exceeded_position_stock]["Exposure"] < 0 else -1
                    Contract=exceeded_position_stock
                    Underlying=exceeded_position_stock
                    Contract_Type="F"
                    Qty=exceeded_amount_in_amount/Price
                    Trading_cost=0
                    Strike_price=0

                    new_adjustment_trades=[Account,Strategy,Date,Price,Side,Contract,Underlying,Contract_Type,Qty,Trading_cost,Strike_price]

                    todays_trade.loc[len(todays_trade)]=new_adjustment_trades
                    adjustment_positions.loc[exceeded_position_stock,"Position"]+=-1*Side*Qty
                    current_positions.loc[exceeded_position_stock,"Position"]+=Qty*Side

            current_positions["Previous_Close_price"]=yesterdays_close_price
            current_positions["Exposure"]=current_positions["Close_price"]*current_positions["Position"]
            current_positions["Exposure_in_perc"]=current_positions["Exposure"]/previous_day_AUM
            current_positions["Gross_exposure_in_perc"]=current_positions["Exposure_in_perc"].abs()
            adjustment_positions.loc["Close_price"]=todays_close_price
            adjustment_positions.loc["Percentage"]=(adjustment_positions["Positions"]*adjustment_positions.loc["Close_price"])/previous_day_AUM

            #update PNL for the day,current positions
            current_position_history.loc[current_day]=current_positions["Position"]
            current_position_exposure.loc[current_day]=current_positions["Exposure"]
            current_position_perc_history.loc[current_day]=current_positions["Exposure_in_perc"]
            adjustments_position_history.loc[current_day]=adjustment_positions["Position"]
            adjustments_position_history_perc.loc[current_day]=adjustment_positions["Percentage"]
            
            portfolio_values.loc[current_day,"net_exposure"]=current_positions["Exposure_in_perc"].sum()
            portfolio_values.loc[current_day,"gross_exposure"]=current_positions["Gross_exposure_in_perc"].sum()
            previous_day_AUM=portfolio_values.loc[current_day,"AUM"]
            
            #add the trades in final trade register
            previous_day=current_day
            final_trade_register=final_trade_register.append(todays_trade)
    
    daily_exposure=daily_exposure.T
    weekly_exposure=weekly_exposure.T
    sn_exposure=sn_exposure.T
    rsi_exposure=rsi_exposure.T
    rsc_exposure=rsc_exposure.T
    ESA_exposure=ESA_exposure.T
    stock_momentum_exposure=stock_momentum_exposure.T
    d90_vol_exposure=d90_vol_exposure.T
    M12_M1_ret_exposure=M12_M1_ret_exposure.T
    SML_ret_exposure=SML_ret_exposure.T
    
    to_be_saved_as_csv=[daily_exposure,weekly_exposure,sn_exposure,rsi_exposure,rsc_exposure,ESA_exposure,stock_momentum_exposure,d90_vol_exposure,M12_M1_ret_exposure,SML_ret_exposure]
    excel_creation(to_be_saved_as_csv,output_folder,"Combined portfolio exposure")
    
    return current_position_history,current_position_exposure,price_data_close_series,current_position_perc_history,adjustments_position_history,adjustments_position_history_perc\
        ,strategy_net_PNL,strategy_net_PNL_perc,strategy_net_exposure,strategy_gross_exposure,portfolio_values,final_trade_register

if __name__=='__main__':
    
    warnings.filterwarnings('ignore')
    
    baseamount=1000000000
    previous_day_AUM=baseamount
    exposure_limit=0.1
    stock_momentum_hedge_required=0
    current_stock_momentum_hedge=0

    portfolio_start_date = datetime.datetime(2010,12,1)
    portfolio_end_date = datetime.datetime(2022, 2, 28)
    portfolio_type="Mean Reversion"

    current_folder_path=Path().absolute().joinpath("Data")

    input_folder_path=Path().absolute().joinpath("Input_files")
    expiry_days_path=current_folder_path/"Expiry days.csv"
    universe_stocks_path=current_folder_path/"Nifty Index members.csv"
    nifty_price_data_path=current_folder_path/"Price_Data/Nifty Index.csv"
    nifty_futures_data_path=current_folder_path/"Price_Data/Nz1 Index.csv"
    nifty_futures2_data_path=current_folder_path/"Price_Data/Nz2 Index.csv"
    cash_data_folder_path=current_folder_path/"Stock Prices CSV"

    futures_1_data_folder_path=current_folder_path/"Futures Prices CSV"
    futures_2_data_folder_path=current_folder_path/"Futures Prices series2 CSV"
    trade_file_path=current_folder_path/"Portfolio_construction/trades_input.csv"

    output_folder="Portfolio_PNL/Iterations1"

    nifty_data=reading_price_data_from_csv(nifty_price_data_path)
    nifty_data= nifty_data[(nifty_data.index>portfolio_start_date) &(nifty_data.index<=portfolio_end_date) ]
    universal_dates=nifty_data.index

    monthly_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="M")
    annual_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="Y")

    price_data=import_all_price_data_from_csv_files(cash_data_folder_path)
    symbol_data=pd.Series(price_data.keys())

    futures_data=import_all_price_data_from_csv_files(futures_1_data_folder_path)
    futures_symbol_data=pd.Series(futures_data.keys())

    futures_2_data=import_all_price_data_from_csv_files(futures_2_data_folder_path)
    futures_2_symbol_data=pd.Series(futures_2_data.keys())

    expiry_days=pd.read_csv(expiry_days_path)
    expiry_days=pd.to_datetime(expiry_days["Expiry days"])
    expiry_days=expiry_days[expiry_days.between(portfolio_start_date,portfolio_end_date)]
    pnl_expiry_series=pd.DataFrame(0,columns=["Baseamount","Cumulative PNL","PNL in INR","PNL in %"],index=expiry_days)

    individual_trade_list=reading_trades_from_csv(trade_file_path)
    individual_trade_list.columns=["Account","Strategy","Date", "Price", "Side", "Contract", "Underlying","Contract_Type", "Qty", "Trading_Cost", "Strike_Price"]

    strategy_details=pd.DataFrame(columns=["Weightage","Stocks","Current_AUM","Stop_Loss"])
    strategy_details.loc["Weekly_MR"]=[0.05,10,0,-1]
    strategy_details.loc["RSI"]=[0.15,10,0,-0.05]
    strategy_details.loc["RSC"] = [0.10, 10, 0, -0.05]
    strategy_details.loc["SN"]=[0.10,10,0,-0.05]
    strategy_details.loc["ESA"]=[0,10,0,-0.05]
    strategy_details.loc["Stock_Momentum"]=[0.20,1,0,-1]
    strategy_details.loc["DailyMR"]=[0.1,10,0,-1]
    strategy_details.loc["90D_Volatility"]=[0.15,10,0,-0.05]
    strategy_details.loc["M12-M1"]=[0.15,10,0,-0.05]
    strategy_details.loc["SML"]=[0.05,10,0,-0.05]

    strategy_details["Current_AUM"]=baseamount*strategy_details["Weightage"]

    current_positions_history, current_position_exposure, price_data_close_series, current_position_perc_history, adjustments_position_history, adjustments_position_history_perc \
        , strategy_net_PNL, strategy_net_PNL_perc, strategy_net_exposure, strategy_gross_exposure, portfolio_values, final_trade_register=combined_portfolio_pnl_generation(universal_dates,expiry_days,baseamount,exposure_limit,strategy_details,price_data,
                                      futures_2_data,individual_trade_list,output_folder)

    saving_dataframes(current_positions_history,"Positions",output_folder)
    saving_dataframes(price_data_close_series,"Closing_prices",output_folder)
    saving_dataframes(current_position_exposure,"Exposure_stock",output_folder)
    saving_dataframes(current_position_perc_history,"Exposure_stock_perc",output_folder)
    saving_dataframes(adjustments_position_history,"Adjustment Positions",output_folder)
    saving_dataframes(adjustments_position_history_perc,"Adjustment_perc",output_folder)
    saving_dataframes(strategy_net_PNL,"Strategy Daily PNL",output_folder)
    saving_dataframes(strategy_net_PNL_perc,"Strategy Daily PNL in %",output_folder)
    saving_dataframes(strategy_net_exposure,"Strategy Net Exposure",output_folder)
    saving_dataframes(strategy_gross_exposure,"Strategy Gross Exposure",output_folder)
    saving_dataframes(portfolio_values,"PNL_series",output_folder)

    final_trade_register["NetQty"]=final_trade_register["Qty"]*final_trade_register["Side"]
    final_trade_register=final_trade_register.groupby(["Date","Contract"])["NetQty"].sum()
    saving_dataframes(final_trade_register,"Trades",output_folder)





