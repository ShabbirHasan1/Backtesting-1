import pandas as pd
from pathlib import Path
from openpyxl import Workbook, load_workbook
from Strategies import roc_system as roc_system
from Strategies import rsi50_system as rsi50_system
import Trades
from Trade_Generation import creating_individual_trade,creating_individual_trade_db
from Strategies import rsi50_system as rsi50
from Trade_Analysis import trade_distribution, trade_summary, rolling_12m_trade_summary
from Trade_Analysis import walkforward_annual_summary
from Timeframe_Manipulation import series_resampling as tm
from PNL_Generation import pnl_generation as pg
import my_funcs
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    baseamount = 10000000
    roc_period1 = 10
    roc_period2 = 25
    roc_period3 = 40
    rsi_period=14

    folder_path = Path().absolute().joinpath("Data\Futures prices CSV")

    wb = load_workbook("Parameters_input_file.xlsx")
    ws=wb.active

    input_parameters = pd.DataFrame(ws.values)

    input_parameters.columns=input_parameters.iloc[0]
    input_parameters.drop(0,inplace=True)

    symbols=input_parameters["Symbols"].tolist()


    price_data = my_funcs.import_price_data_from_csv_files(folder_path, symbols)

    universal_dates = price_data[symbols[1]].index
    individual_trade_list_1 = pd.DataFrame()
    individual_trade_list=pd.DataFrame()
    for i in symbols:
        individual_trade_list_1=individual_trade_list_1.append(roc_system.roc_system(price_data[i], roc_period1, roc_period2, roc_period3,"","Individual",None)[0],ignore_index=True)
        individual_trade_list_1=individual_trade_list_1.append(rsi50_system.rsi50_system(price_data[i], rsi_period,"","Individual",None)[0],ignore_index=True)
        individual_trade_list_1.Contract = i
        individual_trade_list_1.Contract_Type = "F"
        individual_trade_list_1.Qty = individual_trade_list_1.Qty * 1000
        individual_trade_list_1.Trading_Cost = 0.00015
        individual_trade_list=individual_trade_list.append(individual_trade_list_1,ignore_index=True)
        individual_trade_list_1=pd.DataFrame()

    trade_register = creating_individual_trade_db.creating_individual_trade_db(individual_trade_list)

    pnl_series, DD_distribution = pg.pnl_timeseries_multiple_strategy_trade(trade_register, price_data,
                                                                        universal_dates, baseamount)


    trade_data = pd.DataFrame.from_records([x.get_individual_trade_data() for x in trade_register], index="Trade ID")

    trade_data.name="Trade_Data"
    pnl_series.name="PNL_Daily"

    to_be_saved_as_csv = [trade_data, pnl_series]

    my_funcs.excel_creation(to_be_saved_as_csv, "Results/Test Program","Test Program")