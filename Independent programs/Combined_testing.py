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

    symbols=["NZ1 Index"]

    price_data = import_price_data_from_csv_files(data_path, symbols)

    universal_dates = price_data[symbols[0]].index

    pnl_series={}
    trade_statistics={}

    for i in symbols:
        for strategy in strategy_list:
            pnl_series[strategy.Strategy],trade_statistics[strategy.Strategy]=si.single_instrument_single_system(strategy.Strategy,strategy.Period,strategy.Parameters,price_data[i])


    pnl_series=pd.DataFrame(pnl_series)
    trade_statistics=pd.DataFrame(trade_statistics)

    trade_statistics.name="Trade_statistics"
    pnl_series.name="PNL_Daily"

    to_be_saved_as_csv = [trade_statistics, pnl_series]

    excel_creation(to_be_saved_as_csv, "Results/Test Program","Test Program")