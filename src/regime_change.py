"""
This code is based on the code and explanation found here: 
    https://developers.lseg.com/en/article-catalog/article/market-regime-detection?ck_subscriber_id=1970716486

"""
import pandas as pd
import numpy as np
import mplfinance as mpf

from icecream import ic
from loguru import logger as l
from datetime import datetime, date, timedelta

from hmmlearn.hmm import GaussianHMM
import plotly.graph_objects as go
from plotly.graph_objs.scatter.marker import Line
from plotly.subplots import make_subplots
import plotly.express as px
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture
import math
import warnings
warnings.filterwarnings('ignore')


def prepare_data_for_model_input(prices, ma):
    '''
        Input:
        prices (df) - Dataframe of close prices
        ma (int) - legth of the moveing average
        
        Output:
        prices(df) - An enhanced prices dataframe, with moving averages and log return columns
        prices_array(nd.array) - an array of log returns        
    '''    
    # symbol = prices.columns.name
    symbol = prices.columns[0]
    prices[f'{symbol}_ma'] = prices.rolling(ma).mean()
    prices[f'{symbol}_log_return'] = np.log(prices[f'{symbol}_ma']/prices[f'{symbol}_ma'].shift(1)).dropna()
 
    prices.dropna(inplace = True)
    prices_array = np.array([[q] for q in prices[f'{symbol}_log_return'].values])
    
    return prices, prices_array


def plot_hidden_states(hidden_states, prices_df):
    '''
    Input:
    hidden_states(numpy.ndarray) - array of predicted hidden states
    prices_df(df) - dataframe of close prices
    
    Output:
    Graph showing hidden states and prices
    
    '''
    ic(prices_df)
    ic(hidden_states)
    # for i in hidden_states:
        # ic(i)
    colors = ['blue', 'green']
    n_components = len(np.unique(hidden_states))
    ic(n_components)
    fig = go.Figure()
 
    for i in range(n_components):
        mask = hidden_states == i
        ic(mask)
        print('Number of observations for State ', i,":", len(prices_df.index[mask]))
        
        # fig.add_trace(go.Scatter(x=prices_df.index[mask], y=prices_df[f"{prices_df.columns.name}"][mask],
                    # mode='markers', name='Hidden State ' + str(i), marker=dict(size=4,color=colors[i])))
        fig.add_trace(go.Scatter(x=prices_df.index[mask], y=prices_df.iloc[-1],
                    mode='markers', name='Hidden State ' + str(i), marker=dict(size=4,color=colors[i])))
        
    fig.update_layout(height=400, width=900, legend=dict(
            yanchor="top", y=0.99, xanchor="left",x=0.01), margin=dict(l=20, r=20, t=20, b=20)).show()
    

class RegimeDetection:
 
    def get_regimes_hmm(self, input_data, params):
        hmm_model = self.initialise_model(GaussianHMM(), params).fit(input_data)
        return hmm_model
    
    def get_regimes_clustering(self, params):
        clustering =  self.initialise_model(AgglomerativeClustering(), params)
        return clustering
    
    def get_regimes_gmm(self, input_data, params):
        gmm = self.initialise_model(GaussianMixture(), params).fit(input_data)
        return gmm
        
    def initialise_model(self, model, params):
        for parameter, value in params.items():
            setattr(model, parameter, value)
        return model
