import single_instrument_single_system as si
from PNL_Generation import pnl_generation as pg
from my_funcs import *
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    baseamount = 10000000

    folder_path = Path().absolute().joinpath("Input_files")
    data_path=Path().absolute().joinpath("Data/Price_Data")

    strategy_list=reading_list_of_strats_from_excel(folder_path)

    symbols=["AF1 Index"]

    price_data = import_price_data_from_csv_files(data_path, symbols)

    universal_dates = price_data[symbols[0]].index

    pnl_series={}
    trade_statistics={}
    pnl_series_PNL=pd.DataFrame()
    pnl_series_percentage = pd.DataFrame()
    pnl_series_equity = pd.DataFrame()
    pnl_series_dd = pd.DataFrame()
    eod_position=pd.DataFrame()

    for symbol in symbols:

        for strategy in strategy_list:
            price_data_symbol = price_data[symbol].copy()
            try:
                pnl_series[strategy.Strategy],trade_statistics[strategy.Strategy]=si.single_instrument_single_system(strategy.Strategy,strategy.Period,strategy.Parameters,price_data_symbol)
                pnl_series_PNL[strategy.Strategy] = pnl_series[strategy.Strategy]["PNL"]
                eod_position[strategy.Strategy] = pnl_series[strategy.Strategy]["EOD Position"]
                pnl_series_percentage[strategy.Strategy] = pnl_series[strategy.Strategy]["%PNL"]
                pnl_series_equity[strategy.Strategy] = pnl_series[strategy.Strategy]["Equity"]
                pnl_series_dd[strategy.Strategy] = pnl_series[strategy.Strategy]["DD"]

            except:
                print(f"{strategy.Strategy} Not ok!")

    trade_statistics=pd.DataFrame(trade_statistics)

    trade_statistics.name="Trade_statistics"
    pnl_series_PNL.name="PNL_Daily"
    pnl_series_percentage.name="PNL_Daily_%"
    pnl_series_equity.name = "Equity_Curve"
    pnl_series_dd.name="DD"
    eod_position.name="EOD Position"

    to_be_saved_as_csv = [trade_statistics, pnl_series_PNL,pnl_series_percentage,pnl_series_equity,pnl_series_dd,eod_position]

    excel_creation(to_be_saved_as_csv, "Results/Bank Nifty","Bank Nifty")