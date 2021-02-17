'''
this is a collection of several functions to be used across various programs
'''

from pathlib import Path
import pandas as pd
import os
import openpyxl
from collections import namedtuple

# this fuction converts the datetime data in the dataframe to YYYY-mmm-dd format.
# use this function before saving dataframe in excel of csv

def convert_datetime(data_frame):
    cols = data_frame.select_dtypes('datetime64')
    data_frame[cols.columns] = cols.apply(lambda x: x.dt.strftime('%Y-%m-%d'))

    return data_frame

# this function is used to create csv's for each dataframe in the dataframes list
# input: list of dataframes, directory name where csv's have to be stored
# output: no returns, csv's will be created for each dataframe

def csv_creation(data_frames, dir_name):
    output_dir=Path().absolute().joinpath(dir_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in data_frames:
        output_file = i.name + '.csv'
        i.to_csv(output_dir / output_file)  # can join path elements with / operator

# reading price data from csv file at the give location
# input: file path, file must contain Dates, Open, High, Low, close, Volume data
# returns price data: dataframe with price data and date as index

def reading_price_data_from_csv(file_path):
    price_data = pd.read_csv(file_path)
    price_data.set_index("Dates", inplace=True)
    price_data.columns = ["Open", "High", "Low", "Close", "Volume"]
    price_data.index = pd.to_datetime(price_data.index, format="%d-%m-%Y")

    return price_data

# reading trades data from csv file at given location
# input: file location, should have column "Date"
# output: dataframe with trade data

def reading_trades_from_csv(file_path):
    trades = pd.read_csv(file_path, header=0, parse_dates=True)
    trades["Date"] = pd.to_datetime(trades["Date"], format="%d-%m-%Y")

    return trades

# import price data of multiple symbols from a given folder
# input: folder path, symbols
# folder path should containg files with price data of individual instruments
# output: dictionary of dataframes with symbols keyword and price data as dataframe

def import_price_data_from_csv_files(folder_path, symbols):
    price_data = {}

    for symbol in symbols:
        price_data_name = pd.read_csv(folder_path.joinpath( symbol + '.csv'))
        price_data_name.set_index("Dates", inplace=True)
        price_data_name.columns = ["Open", "High", "Low", "Close", "Volume"]
        price_data_name.index = pd.to_datetime(price_data_name.index, format="%d-%m-%Y")

        #cleaning price data
        price_data_name=price_data_name.loc[price_data_name.index.dropna()]
        price_data_name["Volume"].fillna(0,inplace=True)
        price_data_name["Close"].fillna(method="ffill",inplace=True)
        price_data_name.fillna(method="bfill",axis=1,inplace=True)


        price_data[symbol] = price_data_name

    return price_data

# imports the price data from all the files in the given folder
# it first creates a list of name of all the csv files in the folder
# then it send the folder pathe and list to the "import_price_data_from_csv_files" function to extract price data from those files
# input: folder path where price data is available
# output: price data dictionary with symbol as keyword

def import_all_price_data_from_csv_files(folder_path):

    symbols = os.listdir(folder_path)
    symbols = list(filter(lambda f: f.endswith('.csv'), symbols))

    symbols = list(map(lambda x : x.replace(".csv", ""), symbols))

    price_data = import_price_data_from_csv_files(folder_path, symbols)

    return price_data

# creates excel file with dataframes stores in seperate sheets
# input: folder path, data-frames list and excel name
# output: none

def excel_creation(data_frames, dir_name,excel_name):

    output_dir=Path().absolute().joinpath(dir_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_name=excel_name+".xlsx"
    output_file=output_dir/output_file_name

    with pd.ExcelWriter(output_file, engine="openpyxl",datetime_format='DD/MM/YYYY',float_format="#,##0;-#,[RED]#,##0") as writer:
        for n, df in enumerate(data_frames):
            df.to_excel(writer, sheet_name=data_frames[n].name)
        writer.save()

# reading a list of strategies from "Strategies.xlsx" file at the given file pathe
# the output has named tuples with strategies and associated parameter values to be used


def reading_list_of_strats_from_excel(input_file_path):

    input_file_name = "Strategies.xlsx"
    input_file = input_file_path / input_file_name

    strategies=read_from_excel(input_file)

    strategies_data=strategies["Strategies"]


    strategy_list=iternamedtuples(strategies_data)

    return strategy_list

# function helps to map strategy with assocaiated variabkes and parameters
# it creates a list of named tuples where strategy name is assocaited with a
# list containing parameters values to be used


def iternamedtuples(strategies_data):

    strategy=namedtuple("strategy",["Strategy","Period","Parameters"])
    strategy_list=[]
    for row in strategies_data.index:

        period=strategies_data.loc[row][0]

        strategy_1=strategy(row,period,strategies_data.loc[row][1:].tolist())

        strategy_list.append(strategy_1)

    return strategy_list

# function reads from the excel stored at given file path and
# stores data in different sheet in different dataframes

def read_from_excel(input_file_path):

    wb=openpyxl.load_workbook(input_file_path)

    sheet_name=wb.get_sheet_names()
    dataframes={}

    for sheet in sheet_name:
        dataframes[sheet]=pd.DataFrame(wb.get_sheet_by_name(sheet).values)
        dataframes[sheet].columns=dataframes[sheet].iloc[0]
        dataframes[sheet].drop(0,inplace=True)
        dataframes[sheet].set_index(dataframes[sheet].columns[0],drop=True,inplace=True)

    return dataframes


