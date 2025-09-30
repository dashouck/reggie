"""
https://www.tiingo.com/documentation/

# TODO: look into websockets connection instead.
"""
import random
import csv
import os
import requests
import numpy as np
import pandas as pd

# from websocket import create_connection
import simplejson as json
# from icecream import ic
from datetime import datetime, date, timedelta
from loguru import logger as l


current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "./data/")
# l.info(f'data_dir: {data_dir}')

with open(f"{current_dir}/api_token.txt", "r") as file:
    token = file.readline().strip()
    # l.info(f'using token: {token}')
date_format = '%Y-%m-%d' # 2016-10-22


def get_all_data(symbol):
    """
    return entire df for given symbol if data file exists
    """
    file_name = f'{data_dir}{symbol.upper()}.csv'
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name, index_col='date')
        
        return df
    else:
        l.error(f"Error: {file_name} not found.")
        
        return None
    
    
def get_daily_returns(symbol, start_date, end_date):
    """
    return daily returns as a numpy array
    """
    # daily_return = (adj_close_t / adj_close_t-1) - 1
    # pd.pct_change() also accomplishes this
    df = get_data(symbol, start_date, end_date)
    l.info(df)
    df['pct_change'] = df['adjClose'].pct_change()
    
    df = df.dropna()

    # Create a NumPy array containing dates and percentage changes
    # np_array = np.column_stack((df.index, df['pct_change']))
    
    return df['pct_change']
        

def get_data(symbol, start_date, end_date, verbose=False):
    """
    get data from csv files save to system
    """
    file_name = f'{data_dir}{symbol.upper()}.csv'
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name, index_col='date')
            
        if verbose:
            l.info(f'{file_name} loaded')
            l.info(df.shape)
            l.info(df.columns)
            l.info(f'{df.index[0]} - {df.index[-1]}')
            
            if df.isnull().values.any():
                l.info('df contains NaN values')
            else:
                l.info('df has no NaN values')
        
        # check that start_date and end_date are in the range
        # of the existing data file
        start_dt = datetime.strptime(start_date, date_format).date()
        end_dt = datetime.strptime(end_date, date_format).date()
        start_data_dt = datetime.strptime(df.index[0], date_format).date()
        end_data_dt = datetime.strptime(df.index[-1], date_format).date()
        if start_data_dt > start_dt:
            l.error(f'Error: data does NOT extend far enough into past.') 
            l.error(f'start_date: {start_dt} passed in, but data file starts at: {start_data_dt}')
            
        if end_data_dt < end_dt:
            l.info(f'Error: data does NOT extend far enough toward present.')
            l.info(f'end_date: {end_dt} passed in, but data file starts at: {end_data_dt}')

        
        df = df[start_date:end_date]
        df.index = pd.to_datetime(df.index)
        
        df = set_cols_for_backtesting(df)
        
        return df
    else:
        l.error(f"Error: {file_name} not found.")
        
        return None


def get_vix(start_date, end_date, verbose=False):
    """
    return VIX OHLC for the given dates
    """
    file_name = f'{data_dir}VIX.csv'
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name)
        # df['date'] = pd.to_datetime(df['DATE'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
        # df = df.drop('DATE', axis=1)
        # df = df.rename(columns={'OPEN': 'Open', 'HIGH': 'High', 'LOW': 'Low', 'CLOSE': 'Close'})
        df.set_index('date', inplace=True)
        # df.to_csv('modified_file.csv', index=True)
        
        if verbose:
            l.info(f'{file_name} loaded')
            l.info(df.shape)
            l.info(df.columns)
            l.info(f'{df.index[0]} - {df.index[-1]}')
            
            if df.isnull().values.any():
                l.info('df contains NaN values')
            else:
                l.info('df has no NaN values')
        
        df = df[start_date:end_date]
        df.index = pd.to_datetime(df.index)
          
        return df
    else:
        l.error(f"Error: {file_name} not found.")
        
        return None 


def update_vix_to_today():
    """
    update existing data file from last date in data
    file to todays date for vix
    """
    url = 'https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv'
    today_date = date.today()
    l.info(f'updating VIX to {today_date}')
    
    file_name = f'{data_dir}VIX.csv'
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name)
        # df['date'] = pd.to_datetime(df['DATE'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
        # df = df.drop('DATE', axis=1)
        # df = df.rename(columns={'OPEN': 'Open', 'HIGH': 'High', 'LOW': 'Low', 'CLOSE': 'Close'})
        df.set_index('date', inplace=True)
        
        last_date = df.index[-1]
        last_date = datetime.strptime(last_date, date_format).date()
        if last_date < today_date:
            start_date = last_date + timedelta(days=1)
            l.info(url)
            l.info(f"Adding data from {start_date} to {today_date}")
            
            df_new = pd.read_csv(url)
            df_new['date'] = pd.to_datetime(df_new['DATE'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
            df_new = df_new.drop('DATE', axis=1)
            df_new.set_index('date', inplace=True)
            # df_new = df_new.rename(columns={'OPEN': 'Open', 'HIGH': 'High', 'LOW': 'Low', 'CLOSE': 'Close'})
            df_new.columns = ['Open','High','Low','Close']
            # print(df_new)
            df_new = df_new.loc[start_date.strftime('%Y-%m-%d'):today_date.strftime('%Y-%m-%d')]
            
            df_updated = pd.concat([df, df_new], axis=0)
        
            df_updated.to_csv(f'{data_dir}VIX.csv')
        else:
            l.error(f'no data to update for VIX {last_date} - {today_date}')           
    else:
        l.error(f"Error: {file_name} not found.") 
        

def set_cols_for_backtesting(df):
    """
    drop non-adjusted cols, and rename adjusted cols
    to match format expected by backtesting.py
    """
    cols_to_drop = ['close', 'high', 'low', 'open', 'volume', 'divCash', 'splitFactor']
    df = df.drop(cols_to_drop, axis=1)
    
    df = df.rename(columns={'adjClose': 'Close', 'adjHigh': 'High', 'adjLow': 'Low', 'adjOpen': 'Open', 'adjVolume': 'Volume'})

    new_order = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = df.reindex(columns=new_order)

    return df  

  
def dl_and_prepend(symbol, start_date):
    """
    add data to start of existing data file
    """
    df = get_all_data(symbol)
    start_dt = datetime.strptime(start_date, date_format).date()
    data_start_date = df.index[0]
    data_start_dt = datetime.strptime(data_start_date, date_format).date()
    end_date = data_start_dt - timedelta(days=1)
    
    if start_dt < data_start_dt:
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}&endDate={end_date}&token={token}&format=csv"
        l.info(f'{url}')
        res = requests.get(url)

        with open(f'{data_dir}{symbol.upper()}.csv', 'wb') as f:
            f.write(res.content)
            
        with open(f'{data_dir}{symbol.upper()}.csv', 'a') as f:
            df.to_csv(f, index=True, header=False)
        
    else:
        l.error(f'{start_date} is > {data_start_date}')
        l.error(f'nothing to prepend to data file.')


def update_to_today(symbol):
    """
    update existing data file from last date in data
    file to todays date.
    """
    today_date = date.today()
    l.info(f'updating {symbol} to {today_date}')
    
    file_name = f'{data_dir}{symbol.upper()}.csv'
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name, index_col='date')
        
        last_date = df.index[-1]
        last_date = datetime.strptime(last_date, date_format).date()
        if last_date < today_date:
            start_date = last_date + timedelta(days=1)
            url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}&endDate={today_date}&token={token}&format=csv"
            l.info(url)
            res = requests.get(url)
            
            # remove header line
            response_content = res.content.decode('utf-8')
            lines = response_content.split('\n')[1:]
            # new_data = '\n' + '\n'.join(lines)
            new_data = '\n'.join(lines)
            
            with open(f'{data_dir}/{symbol.upper()}.csv', 'ab') as f:
                # f.write(res.content)
                f.write(new_data.encode('utf-8'))
        else:
            l.error(f'no data to update for {symbol} {last_date} - {today_date}')           
    else:
        l.error(f"Error: {file_name} not found.") 

        
def dl_daily(symbol, start_date, end_date, isCrypto=False):
    """
    download to new data file
    """
    symbol = symbol
    start_date = start_date # '2010-01-01'
    end_date = end_date
    
    l.info(f'downloading data to file')
    l.info(f'{symbol} - {start_date} to {end_date}')

    if isCrypto:
        url = f"https://api.tiingo.com/tiingo/crypto/prices?tickers={symbol}&startDate={start_date}&endDate={end_date}&resampleFreq=5min&token={token}&format=csv"
    # elif isHourly:
        # url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}&endDate={end_date}&resampleFreq=1hour&token={token}&format=csv"
    else:
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date}&endDate={end_date}&token={token}&format=csv"

    l.info(f'connecting to: {url}')
    res = requests.get(url)
    
    file_name = f"{symbol.upper()}.csv"
    l.info(f'writing file: {file_name}')
    with open(f"{data_dir}{file_name}", 'wb') as f:
        f.write(res.content)


def get_rand_quote():
    file_path = 'quotes.txt'
    with open(file_path, 'r') as file:
        quotes = file.readlines()
    return random.choice(quotes).strip()


def load_tickers():
    with open(data_dir + '../tickers.txt', 'r') as file:
        tickers = file.read().splitlines()
    
    for ticker in tickers:
        # check if data file exists
        if os.path.exists(f"{data_dir}{ticker}"):
            pass
        else:
            # no datafile, let's try to download the data
            dl_daily(ticker, '1995-01-01', datetime.now().strftime(date_format))
            
    return [{'label': ticker, 'value': ticker} for ticker in tickers]


if __name__=="__main__":

    # 
    # test setting cols to backtesting.py standard
    symbols = ['GLD', 'META']
    start_date = '1997-01-01'
     # end_date = '2024-01-01'
    today = datetime.now().strftime(date_format)
    for symbol in symbols:
        dl_daily(symbol, start_date, today)
        df = get_data(symbol, start_date, today)
        l.info(df.head())
    # df = set_cols_for_backtesting(df)
    # ic(df.head())
    
    # 
    # test updating vix to today
    # update_vix_to_today()
    # today = datetime.now().strftime(date_format)
    # df = get_vix('2024-01-01', today)
    # print(df)
    
    # 
    # test downloading crypto data to file
    #symbol = 'solusd'
    #start_date = '2024-01-01'
    #today = datetime.now().strftime(date_format)
    # dl_data_tofile(symbol, start_date, today, isCrypto=True)
    
    # 
    # test daily returns
    #symbol = 'META'
    #start_date = '2024-01-01'
    #end_date = '2025-09-24'
    #data = get_daily_returns(symbol, start_date, end_date)
    #ic(data)
    
    # 
    # test update to today's price
    # update_to_today('GLD')
    
