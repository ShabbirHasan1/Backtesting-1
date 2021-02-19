import pandas as pd
import numpy as sp
import warnings
from my_funcs import *

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    folder_path = Path().absolute().joinpath("Input_files")
    data_path = Path().absolute().joinpath("Data/Price_Data")
    symbols = ["AF1 Index"]

    price_data = import_price_data_from_csv_files(data_path, symbols)

    for symbol in symbols:
        for period in range(2,51,2):




