import pandas as pd
from pathlib import Path

from Strategies import roc_system as roc_system
from Strategies import rsi50_system as rsi50

from Trade_Analysis import trade_distribution, trade_summary, rolling_12m_trade_summary
from Trade_Analysis import walkforward_annual_summary
from Timeframe_Manipulation import series_resampling as tm
from PNL_Generation import pnl_generation as pg
import my_funcs
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    symbol = "NZ1 Index"

    file_path = Path().absolute().joinpath("Data/Price_data")

    price_data = pd.read_csv(file_path.joinpath(symbol + ".csv"))
    price_data.set_index("Dates", inplace=True)
    price_data.columns = ["Open", "High", "Low", "Close", "Volume"]
    price_data.index = pd.to_datetime(price_data.index, format="%d-%m-%Y")

    period = 10
    period1 = 25
    period2 = 40

    initial_capital = 1000000

    trading_cost = 0.0001

    trades_roc = roc_system.roc_system(price_data, period, period1, period2)

    trades_rsi = rsi50.rsi50_system(price_data, period)

    trades = trades_rsi + trades_roc

    trade_summary_data = trade_summary.trade_summary(trades)

    trades_table = trade_summary.trade_data_table(trades)

    trades_12m_rolling_summary = rolling_12m_trade_summary.rolling_12m_trade_summary(trades, price_data)

    walk_forward_annual_summary = walkforward_annual_summary.walkforward_trade_summary(trades, price_data)

    trades_table_csv = my_funcs.convert_datetime(trades_table)
    trades_table_csv.to_csv("Trade Data.csv", index=True)

    trade_summary_data.to_csv("Trade Summary.csv", index=True)

    trade_distribution, freq_dist = trade_distribution.trade_distribution(trades_table)

    pnl_series,DD_distribution = pg.pnl_timeseries_same_value_trade(trades, price_data, initial_capital)

    pnl_series, DD_distribution = pg.pnl_timeseries_monthly_rebalance(trades, price_data, initial_capital)

    pnl_series.to_csv("PNL.csv", index=True)

    pnl_series_monthly = pd.DataFrame(columns=["PNL", "DD"])
    pnl_series_annual = pd.DataFrame(columns=["PNL", "DD"])

    pnl_series_monthly["PNL"] = pnl_series["%PNL"].resample("M").sum()
    pnl_series_monthly["DD"], *_ = pg.DD_sum(pnl_series_monthly["PNL"].cumsum(), 1)

    pnl_series_monthly_rolling_12m = pnl_series_monthly["PNL"].rolling(12).sum()
    pnl_series_monthly_rolling_12m.fillna(0, inplace=True)

    pnl_series_annual["PNL"] = pnl_series["%PNL"].resample("Y").sum()
    pnl_series_annual["DD"], *_ = pg.DD_sum(pnl_series_annual["PNL"].cumsum(), 1)

    pnl_series_monthly.to_csv("Monthly PNL.csv", index=True)

    DD_distribution.to_csv("DD Data.csv", index=True)
