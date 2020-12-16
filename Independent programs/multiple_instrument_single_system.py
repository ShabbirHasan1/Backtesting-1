import pandas as pd

from Strategies import wma20_macd_system as system
from Trade_Analysis import trade_distribution, trade_summary, rolling_12m_trade_summary
from Trade_Analysis import walkforward_annual_summary
from Timeframe_Manipulation import series_resampling as tm
from PNL_Generation import pnl_generation as pg
import my_funcs
from pathlib import Path
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    system_name="20wma_macd_Daily"
    underlying="Stocks"

    folder_path = Path().absolute().joinpath("Data/Stock prices CSV")
    nifty_path=Path().absolute().joinpath("Data/price_Data/Nifty Index.csv")

    nifty_data=my_funcs.reading_price_data_from_csv(nifty_path)

    universal_dates=nifty_data.index

    monthly_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="M")
    annual_index=pd.date_range(universal_dates[0],universal_dates[-1],freq="Y")



    price_data = my_funcs.import_all_price_data_from_csv_files(folder_path)

    symbols = price_data.keys()

    initial_capital = 1000000
    trading_cost = 0.0000

    trade_summary_data = pd.DataFrame(columns=["Total Trades", "Profit Factor", "Total Profit", "Average Profit", "Max Profit",
                                   "Min Profit", "Average Duration", "Hit Ratio", "Profitability", "Max DD in Trade",
                                   "Max Profit in Trade", "Max Loss in Trade", "Max Recovery in Trade",
                                   "Max DD Duration in Trade"])
    trades_table = {}
    trades_12m_rolling_summary = {}
    walk_forward_annual_summary={}
    trade_distribution={}
    freq_dist={}
    #pnl_series_full_data={}
    pnl_series={}
    DD_distribution={}
    pnl_series_monthly={}
    pnl_series_annual={}
    pnl_series_monthly_rolling_12m={}

    period_1 = 20


    for symbol in symbols:

        print(f"Trades for {symbol}")

        trades, _ = system.wma20_macd_system(price_data[symbol], period_1, period="")

        trade_summary_data_full = trade_summary.trade_summary(trades)

        trades_table[symbol] = trade_summary.trade_data_table(trades)

        trade_summary_data.loc[symbol] = trade_summary_data_full.loc["ALL Trades"]

        #pnl_series,DD_distribution = pg.pnl_timeseries_same_value_trade(trades, price_data, 1000000)

        pnl_series_full_data, DD_distribution = pg.pnl_timeseries_monthly_rebalance(trades, price_data[symbol], 1000000)

        pnl_series[symbol] = pnl_series_full_data["%PNL"]

        pnl_series_monthly[symbol] = pd.DataFrame(columns=["PNL"])
        pnl_series_annual[symbol] = pd.DataFrame(columns=["PNL"])

        pnl_series_monthly[symbol] = pnl_series[symbol].resample("M").sum()
        #pnl_series_monthly[symbol]["DD"], *_ = pg.DD_sum(pnl_series_monthly["PNL"].cumsum(), 1)

        pnl_series_monthly_rolling_12m[symbol] = pnl_series_monthly[symbol].rolling(12).sum()
        pnl_series_monthly_rolling_12m[symbol].fillna(0, inplace=True)

        pnl_series_annual[symbol] = pnl_series[symbol].resample("Y").sum()
        #pnl_series_annual[symbol]["DD"], *_ = pg.DD_sum(pnl_series_annual[symbol]["PNL"].cumsum(), 1)


    #trades_table_csv = my_funcs.convert_datetime(trades_table)
    #trades_table_csv.to_csv("Trade Data.csv", index=True)

    #DD_distribution=pd.DataFrame(DD_distribution)
    pnl_series=pd.DataFrame(pnl_series,index=universal_dates)
    pnl_series.fillna(0,inplace=True)



    pnl_series_monthly=pd.DataFrame(pnl_series_monthly,index=monthly_index)
    pnl_series_monthly.fillna(0,inplace=True)
    pnl_series_annual=pd.DataFrame(pnl_series_annual,index=annual_index)
    pnl_series_annual.fillna(0, inplace=True)

    #trades_table_csv.name = "trades_table_csv"
    trade_summary_data.name = "trade_summary_data"
    pnl_series.name = "pnl_series"
    pnl_series_monthly.name = "pnl_series_monthly"
    pnl_series_annual.name = "pnl_series_annual"
    #DD_distribution.name = "DD_distribution"

    to_be_saved_as_csv = [trade_summary_data, pnl_series, pnl_series_monthly, pnl_series_annual]

    output_folder=system_name+"/"+underlying

    #my_funcs.csv_creation(to_be_saved_as_csv, "Results/"+output_folder)
    my_funcs.excel_creation(to_be_saved_as_csv, "Results/"+output_folder, underlying )