import pandas as pd
import numpy as sp
import warnings
from my_funcs import *
from Strategies import periodic_reversal_system

from Trade_Analysis import trade_distribution, trade_summary, rolling_12m_trade_summary
from Trade_Analysis import walkforward_annual_summary
from PNL_Generation import pnl_generation as pg

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    folder_path = Path().absolute().joinpath("Input_files")
    data_path = Path().absolute().joinpath("Data/Price_Data")
    result_path=Path().absolute().joinpath("results/periodic_reversal")
    symbols = ["NZ1 Index"]

    price_data = import_price_data_from_csv_files(data_path, symbols)

    initial_capital = 1000000
    trading_cost = 0
    PNL_daily=pd.DataFrame()
    PNL_monthly=pd.DataFrame()

    for symbol in symbols:
        for period in range(2,51,2):
            trades,_= periodic_reversal_system.periodic_reversal_system(price_data[symbol],period)
            trade_summary_data = trade_summary.trade_summary(trades)
            trades_table = trade_summary.trade_data_table(trades)
            pnl_series, _ = pg.pnl_timeseries_monthly_rebalance(trades, price_data[symbol], 1000000)

            PNL_daily[str(period)+"period"]=pnl_series["%PNL"]
            PNL_monthly[str(period)+"period"] = pnl_series["%PNL"].resample("M").sum()

    PNL_daily.name="PNL_Daily"
    PNL_monthly.name = "PNL_Monthly"

    to_be_saved_as_csv = [PNL_daily,PNL_monthly]

    excel_creation(to_be_saved_as_csv, result_path,"Nifty")









