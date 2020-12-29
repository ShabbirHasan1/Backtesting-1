import pandas as pd
from pathlib import Path
from Timeframe_Manipulation import series_resampling
import my_funcs
import warnings

if __name__ == '__main__':
    warnings.filterwarnings("ignore")


    folder_path = Path().absolute().joinpath("Data\Price_Data")

    symbols = ["Nifty Index"]

    price_data = my_funcs.import_price_data_from_csv_files(folder_path, symbols)

    price_data_monthly=series_resampling.price_series_periodic(price_data[symbols[0]],period="M")

    price_data_monthly.to_csv("Nifty Monthly.csv", index=True)

