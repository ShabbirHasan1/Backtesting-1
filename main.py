import pandas as pd
from pathlib import Path
from Strategies import roc_system as roc_system
from Strategies import rsi50_system as rsi50_system
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

    folder_path = Path().absolute().joinpath("Data")

    symbols = ["NZ1 Index", "Nifty Index"]

    price_data = my_funcs.import_price_data_from_csv_files(folder_path, symbols)

    universal_dates = price_data[symbols[1]].index

    individual_trade_list = roc_system.roc_system(price_data[symbols[1]], roc_period1, roc_period2, roc_period3,"Individual",price_data[symbols[0]])
    individual_trade_list = individual_trade_list.append(rsi50_system.rsi50_system(price_data[symbols[1]], rsi_period,"Individual",price_data[symbols[0]]),ignore_index=True)

    individual_trade_list.Contract = symbols[0]
    individual_trade_list.Contract_Type = "F"
    individual_trade_list.Qty = individual_trade_list.Qty*1000
    individual_trade_list.Trading_Cost = 0.00015

    trade_register = creating_individual_trade_db.creating_individual_trade_db(individual_trade_list)

    pnl_series, DD_distribution = pg.pnl_timeseries_multiple_strategy_trade(trade_register, price_data,
                                                                        universal_dates, baseamount)

    pnl_series.to_csv("PNL Series New.csv", index=True)

    trade_data = pd.DataFrame.from_records([x.get_individual_trade_data() for x in trade_register], index="Trade ID")
    trade_data.to_csv("Sample Trade Data.csv", index=True)


