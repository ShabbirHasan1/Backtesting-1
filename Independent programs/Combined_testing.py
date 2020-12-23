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


    for i in symbols:
        for strategy in strategy_list:
            pnl_series=si.single_instrument_single_system(strategy.Strategy,strategy.Period,strategy.Parameters,price_data[i])



    trade_register = creating_individual_trade_db.creating_individual_trade_db(individual_trade_list)

    pnl_series, DD_distribution = pg.pnl_timeseries_multiple_strategy_trade(trade_register, price_data,
                                                                        universal_dates, baseamount)


    trade_data = pd.DataFrame.from_records([x.get_individual_trade_data() for x in trade_register], index="Trade ID")

    trade_data.name="Trade_Data"
    pnl_series.name="PNL_Daily"

    to_be_saved_as_csv = [trade_data, pnl_series]

    excel_creation(to_be_saved_as_csv, "Results/Test Program","Test Program")