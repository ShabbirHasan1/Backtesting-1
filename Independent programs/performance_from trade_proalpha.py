import pandas as pd
from pathlib import Path
import collections
from Trade_Generation import creating_individual_trade, creating_individual_trade_db
from Timeframe_Manipulation import series_resampling as tm
from PNL_Generation import pnl_generation as pg
import my_funcs
import warnings
'''
need to update the symbolas and segregate the price series to be sent for pnl calculation
'''
if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    baseamount = 10000000

    current_folder_path = Path().absolute().joinpath("Data")
    nifty_price_data = current_folder_path / "Price_Data/Nifty Index.csv"
    trade_file_path = current_folder_path / "trade_data_sample.csv"


    Nifty_Data = pd.read_csv(nifty_price_data, header=0)
    Nifty_Data.set_index("Dates", inplace=True)

    universal_dates = Nifty_Data.index

    individual_trade_list = my_funcs.reading_trades_from_csv(trade_file_path)

    individual_trade_list.columns = ["Account", "Strategy", "Date", "Price", "Side", "Contract", "Contract_Type",
                                     "Lots", "Lot_Size", "Qty", "Trading_Cost", "Strike_Price"]

    account_list = individual_trade_list["Account"].unique()
    strategy_list = individual_trade_list["Strategy"].unique()
    symbols = individual_trade_list["Contract"].unique()


    price_data = my_funcs.import_price_data_from_csv_files(current_folder_path / "Price_Data", symbols)

    pnl_series = collections.defaultdict(dict)

    for account in account_list:
        for strategy in strategy_list:
            trade_list_to_pass = individual_trade_list[
                (individual_trade_list["Account"] == account) & (individual_trade_list["Strategy"] == strategy)]
            trade_list_to_pass.drop(["Account","Strategy"],axis=1,inplace=True)
            trade_list_to_pass.reset_index(inplace=True)

            trade_register = creating_individual_trade_db.creating_individual_trade_db(trade_list_to_pass)

            pnl_series[account][strategy], _ = pg.pnl_timeseries_multiple_strategy_trade(trade_register, price_data,
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
    pnl_series.name = "PNL Series New"
    trade_data.name = "Sample Trade Data"

    to_be_saved_as_csv = [pnl_series_monthly, pnl_series, trade_data]

    my_funcs.excel_creation(to_be_saved_as_csv, "Pro_Alpha_PNL", "trial.xlsx")
    my_funcs.csv_creation(to_be_saved_as_csv, "Pro_Alpha_PNL")
