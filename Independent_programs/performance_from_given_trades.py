import pandas as pd
from pathlib import Path
from Trade_Generation import creating_individual_trade,creating_individual_trade_db
from Timeframe_Manipulation import series_resampling as tm
from PNL_Generation import pnl_generation as pg
import my_funcs
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    baseamount = 10000000
    current_folder_path =  Path().absolute().joinpath("Data")
    trade_file_path=current_folder_path / "Sample Trades.csv"


    price_data_path = current_folder_path/"Price_Data"

    underlying_name = "example_PNL_from_trade"

    symbols = ["NZ1 Index", "Nifty Index"]

    price_data = my_funcs.import_price_data_from_csv_files(price_data_path, symbols)

    universal_dates = price_data[symbols[1]].index

    individual_trade_list = my_funcs.reading_trades_from_csv(trade_file_path)

    individual_trade_list.columns=["Date","Price","Side","Contract","Contract_Type","Qty","Trading_Cost","Strike_Price"]

    trade_register = creating_individual_trade_db.creating_individual_trade_db(individual_trade_list)

    pnl_series, DD_distribution = pg.pnl_timeseries_multiple_strategy_trade(trade_register, price_data,
                                                                        universal_dates, baseamount)


    trade_data = pd.DataFrame.from_records([x.get_individual_trade_data() for x in trade_register], index="Trade ID")

    pnl_series_monthly = pd.DataFrame(columns=["PNL", "DD"])
    pnl_series_annual = pd.DataFrame(columns=["PNL", "DD"])

    pnl_series_monthly["PNL"] = pnl_series["Cumulative PNL%"].resample("M").sum()
    pnl_series_monthly["DD"], *_ = pg.DD_sum(pnl_series_monthly["PNL"].cumsum(), 1)

    pnl_series_monthly["_rolling_12m"] = pnl_series_monthly["PNL"].rolling(12).sum()
    pnl_series_monthly["_rolling_12m"].fillna(0, inplace=True)

    pnl_series_annual["PNL"] = pnl_series["Cumulative PNL%"].resample("Y").sum()
    pnl_series_annual["DD"], *_ = pg.DD_sum(pnl_series_annual["PNL"].cumsum(), 1)

    pnl_series_monthly.name = "Monthly PNL"
    pnl_series.name= "PNL Series New"
    DD_distribution.name= "DD Data"
    trade_data.name="Sample Trade Data"

    to_be_saved_as_csv = [pnl_series_monthly , pnl_series, DD_distribution , trade_data ]

    my_funcs.excel_creation(to_be_saved_as_csv, underlying_name, "trial.xlsx" )
    my_funcs.csv_creation(to_be_saved_as_csv, underlying_name)



