
import pandas as pd
from pathlib import Path

from Strategies import breakout_system as system
from Trade_Analysis import trade_distribution, trade_summary, rolling_12m_trade_summary
from Trade_Analysis import walkforward_annual_summary
from PNL_Generation import pnl_generation as pg
import my_funcs
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    symbol = "Nz1 Index"

    file_path = Path().absolute().joinpath("Data/Price_data")

    price_data = pd.read_csv(file_path.joinpath(symbol + ".csv"))
    price_data.set_index("Dates", inplace=True)
    price_data.columns = ["Open", "High", "Low", "Close", "Volume"]
    price_data.index = pd.to_datetime(price_data.index, format="%d-%m-%Y")

    underlying_name = "Results/Breakout_Daily"+"/NZ1 Index"

    period_1=50
    period_2=2
    stop_level=3

    initial_capital = 1000000
    trading_cost = 0.0000

    trades, price_signal = system.breakout_system(price_data,period="")

    trade_summary_data = trade_summary.trade_summary(trades)

    trades_table = trade_summary.trade_data_table(trades)

    trades_12m_rolling_summary = rolling_12m_trade_summary.rolling_12m_trade_summary(trades, price_data)

    walk_forward_annual_summary = walkforward_annual_summary.walkforward_trade_summary(trades, price_data)

    trade_distribution, freq_dist = trade_distribution.trade_distribution(trades_table)

    # pnl_series,DD_distribution = pg.pnl_timeseries_same_value_trade(trades, price_data, 1000000)

    pnl_series, DD_distribution = pg.pnl_timeseries_monthly_rebalance(trades, price_data, 1000000)

    pnl_series_monthly = pd.DataFrame(columns=["PNL", "DD"])
    pnl_series_annual = pd.DataFrame(columns=["PNL", "DD"])

    pnl_series_monthly["PNL"] = pnl_series["%PNL"].resample("M").sum()
    pnl_series_monthly["DD"], *_ = pg.DD_sum(pnl_series_monthly["PNL"].cumsum(), 1)

    pnl_series_monthly_rolling_12m = pnl_series_monthly["PNL"].rolling(12).sum()
    pnl_series_monthly_rolling_12m.fillna(0, inplace=True)

    pnl_series_annual["PNL"] = pnl_series["%PNL"].resample("Y").sum()
    pnl_series_annual["DD"], *_ = pg.DD_sum(pnl_series_annual["PNL"].cumsum(), 1)

    trades_table_csv = my_funcs.convert_datetime(trades_table)

    price_signal.name="price_signal"
    trades_table_csv.name = "trades_table"
    trade_summary_data.name = "trade_summary_data"
    pnl_series.name = "pnl_series"
    pnl_series_monthly.name = "pnl_series_monthly"
    pnl_series_annual.name = "pnl_series_annual"
    DD_distribution.name = "DD_distribution"
    trades_12m_rolling_summary.name="Rolling 12 month analysis"
    walk_forward_annual_summary.name="Walk forward analysis"

    Dataframes_to_be_saved_as_csv = [price_signal,trades_table, trade_summary_data, pnl_series, pnl_series_monthly,
                                     pnl_series_annual, DD_distribution,trades_12m_rolling_summary,walk_forward_annual_summary]

    #my_funcs.csv_creation(Dataframes_to_be_saved_as_csv, underlying_name)
    my_funcs.excel_creation(Dataframes_to_be_saved_as_csv, underlying_name, symbol)
