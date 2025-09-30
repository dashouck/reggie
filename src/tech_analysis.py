import pandas as pd
import numpy as np
import pandas_ta as ta
import regime_change as rc

def regime_change(df, symbol):
    prices = pd.DataFrame(columns=['Date', symbol])
    prices[symbol] = df['Close']
    prices['Date'] = df.index
    prices.reset_index(drop=True, inplace=True)
    prices.set_index('Date', inplace=True)

    # print(prices)
    prices, prices_array = rc.prepare_data_for_model_input(prices, 7)
    # print(prices)
    # print(prices_array)
    
    regime_detection = rc.RegimeDetection()   
    params = {'n_components':2, 'covariance_type':"full", 'random_state':100}
 
    hmm_model = regime_detection.get_regimes_hmm(prices_array, params)
    hmm_states = hmm_model.predict(prices_array)

    prices.rename(columns={symbol: 'Close'}, inplace=True)
    df_hmm = pd.DataFrame(index=prices.index)
    df_hmm['states'] = hmm_states
    df_hmm['Close'] = prices['Close']
    # print(df_hmm)
    
    df = df.join(df_hmm['states'])
    #df.to_csv('__test.csv')
    
    return df


def tech_analysis(df):
    """
    add technical analysis columns to the passed in df
    """
    # if symbol is None:
    # df = dat.get_data('SPY', start_date_max, end_date)
    # start_date = df.index.min().strftime(date_format)
    # end_date = df.index.max().strftime(date_format)
    
    # 
    # technical analysis
    df['20_SMA'] = ta.sma(df['Close'], length=20)
    df['50_SMA'] = ta.sma(df['Close'], length=50)
    df['100_SMA'] = ta.sma(df['Close'], length=100)
    df['200_SMA'] = ta.sma(df['Close'], length=200)
    
    # df['golden_crosses'] = 0
    df['golden_cross'] = ((df['50_SMA'].shift(1) < df['200_SMA'].shift(1)) & 
                               (df['50_SMA'] > df['200_SMA'])).astype(int) 
    
    # df['death_crosses'] = 0
    df['death_cross'] = ((df['50_SMA'].shift(1) > df['200_SMA'].shift(1)) & 
                              (df['50_SMA'] < df['200_SMA'])).astype(int)
    #df.to_csv('___death-crosses.csv')
    
    
    
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    df = df.join(stoch)
    df = df.rename(columns={'STOCHk_14_3_3': 'StochK', 'STOCHd_14_3_3': 'StochD'})
    
    bollinger = ta.bbands(df['Close'], length=20, std=2)

    # pandas_ta changed the band column names in 0.3.15+ to include an
    # additional ``_2.0`` suffix, so resolve them dynamically instead of
    # hardcoding the exact strings.
    lower_col = next((col for col in bollinger.columns if col.startswith('BBL_')), None)
    upper_col = next((col for col in bollinger.columns if col.startswith('BBU_')), None)
    middle_col = next((col for col in bollinger.columns if col.startswith('BBM_')), None)
    percent_col = next((col for col in bollinger.columns if col.startswith('BBP_')), None)

    if not all([lower_col, upper_col, middle_col]):
        raise KeyError(f"Unexpected Bollinger column names: {list(bollinger.columns)}")

    if percent_col:
        df['PercentB'] = bollinger[percent_col]
    else:
        df['PercentB'] = (df['Close'] - bollinger[lower_col]) / (bollinger[upper_col] - bollinger[lower_col])

    df = df.join(bollinger)
    df = df.rename(columns={
        lower_col: 'BollingerLower',
        upper_col: 'BollingerUpper',
        middle_col: 'BollingerMiddle'
    })
    
    macd = ta.macd(df['Close'])
    df = df.join(macd)
    df = df.rename(columns={'MACD_12_26_9': 'MACD', 'MACDh_12_26_9': 'MACDH', 'MACDs_12_26_9': 'MACDS'})
    
    return df
