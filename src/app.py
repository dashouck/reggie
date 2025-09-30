"""
this is the main entry point for the plotly
version of the ui

TODO: lookup how to use 20/50/100 day sma
"""
import pandas as pd
import numpy as np
import mplfinance as mpf
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, html, ctx, dash_table, dcc, callback, Output, Input
from loguru import logger as l
from datetime import datetime, date, timedelta

import data as dat
import tech_analysis as ta


# init dash app
app = Dash()

symbol = 'SPY'
start_date = '1997-01-02'
start_date_max = '1995-01-01'

date_format = '%Y-%m-%d' # 2016-10-22
today = datetime.now().strftime(date_format)
end_date = today

date_format = '%Y-%m-%d' # 2016-10-22

# dat.dl_daily(symbol, start_date, end_date)
df = dat.get_data(symbol, start_date, end_date)
df = ta.tech_analysis(df)
df = ta.regime_change(df, 'SPY')

df_vix = dat.get_vix(start_date, end_date)

# update_to_present = False
# if update_to_present == True:
#     dat.update_to_today(symbol)
#     dat.update_vix_to_today()

# 
# app layout
# 
app.layout = [
    html.Div(id='quote-div', children=f"This is the initial quote"),
    html.Div(
        html.Button('Next Quote', id='quote-button', className='btn', n_clicks=0),
        style={'margin-top': '20px',
               'margin-bottom': '20px'
               }
    ),
    dcc.Dropdown(
        id='stock-dropdown',
        options=dat.load_tickers(),
        # options=[
        #     {'label': 'SPY', 'value': 'SPY'},
        #     {'label': 'AAPL', 'value': 'AAPL'},
        #     {'label': 'CMG', 'value': 'CMG'},
        #     {'label': 'NVDA', 'value': 'NVDA'}
        # ],
        value='SPY'  # Default value
    ),
    html.Div(id='dropdown-output-container'),
    dcc.Dropdown(
        id='duration-dropdown',
        options=[
            {'label': '1 Week', 'value': '1W'},
            {'label': '1 Month', 'value': '1M'},
            {'label': '3 Months', 'value': '3M'},
            {'label': 'YTD', 'value': 'YTD'},
            {'label': '1 Year', 'value': '1Y'},
            {'label': '3 Year', 'value': '3Y'},
            {'label': '5 Year', 'value': '5Y'},
            {'label': '10 Year', 'value': '10Y'},
        ],
        value='1M'  # Default value
    ),
    html.Div(
        dcc.RangeSlider(
            id='range-slider',
            # min=0,
            # max=len(df) - 1,
            # value=[len(df) - 1 - 365, len(df) - 1],
            # marks={i: str(date.date().year) for i, date in enumerate(df.index) if i % 365 == 0},
            step=1,
            # tooltip={"placement": "bottom", "always_visible": True}
        ),
        className='range-slider-container'
    ),   
    # html.Div(id='output-range-slider'),
    html.Div(id='date-range-div'),
    dcc.Graph(id='candle-graph'),
    dcc.Graph(id='sma-graph'), 
    dcc.Graph(id='volume-graph'), 
    dcc.Graph(id='sma-quarter-graph'),  
    dcc.Graph(id='vix-graph'), 
    dcc.Graph(id='regime-graph'),
    dcc.Graph(id='bollinger-graph'),
    dcc.Graph(id='stoch-osc-graph'),
    dcc.Graph(id='rsi-graph'),
    dcc.Graph(id='macd-graph'),
    # dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'], value='lifeExp', id='controls-and-radio-item'),
    # dash_table.DataTable(data=df.to_dict('records'), page_size=6),
    # dcc.Graph(figure={}, id='controls-and-graph')
]

app.css.append_css({"external_url": "/assets/styles.css"})


@callback(
    Output('quote-div', 'children'),
    Input('quote-button', 'n_clicks')
)
def update_quotation(btn):
    """
    button callback
    """
    msg = dat.get_rand_quote()
        
    return html.Div(msg)


def update_df(symbol):
    """
    
    """
    global df, start_date
    
    l.info(f"new symbol: {symbol}")
    start_date = start_date_max
    df = dat.get_data(symbol, start_date, end_date)
    start_date = df.index[0].strftime(date_format)
    l.info(f"new start_date: {start_date}")
    
    last_date = df.index[-1]
    # last_date = datetime.strptime(last_date, date_format).date()
    if last_date.date() < datetime.strptime(end_date, date_format).date():
        l.info(f'updating data for {symbol} to {end_date}')
        dat.update_to_today(symbol)
        dat.update_vix_to_today()
        df = dat.get_data(symbol, start_date, end_date)
        
        
    
    l.info(f"new date range: {start_date} - {end_date}")
    
    df = ta.tech_analysis(df)
    df = ta.regime_change(df, symbol)


@app.callback(
    Output('range-slider', 'min'),
    Output('range-slider', 'max'),
    Output('range-slider', 'value'),
    Output('range-slider', 'marks'),
    Input('stock-dropdown', 'value'),
    Input('duration-dropdown', 'value')
    # Input('range-slider', 'value')
)
def update_slider(symbol, selected_duration):
    global start_date
    
    update_df(symbol)
    
    marks = {i: str(date.date().year) for i, date in enumerate(df.index) if i % 365 == 0}
    # print(value_prev)
    # if value_prev[0] < range[0]:
        # value[0] = value_prev[0]
        
    if selected_duration == '1W':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(weeks=1)
    elif selected_duration == '1M':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(months=1)
    elif selected_duration == '3M':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(months=3)
    elif selected_duration == 'YTD':
        start_date_range = pd.Timestamp(f'{pd.Timestamp.now().year}-01-01')
    elif selected_duration == '1Y':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(years=1)
    elif selected_duration == '3Y':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(years=3)
    elif selected_duration == '5Y':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(years=5)
    elif selected_duration == '10Y':
        start_date_range = pd.Timestamp.now() - pd.DateOffset(years=10)

    else:
        # default to one month
        start_date_range = pd.Timestamp.now() - pd.DateOffset(months=1)

    start_timestamp = df.index.asof(start_date_range)
    start_date = start_timestamp.strftime(date_format)
    start_index = df.index.get_loc(start_timestamp)
    
    end_index = len(df) - 1
    
    range = [start_index, end_index]
    l.info(f"range: {range}")
    # range = [len(df) - 1 - 365, len(df) - 1]
        
    # return 0, len(df) - 1, [len(df) - 1 - 365, len(df) - 1], marks
    return 0, len(df) - 1, range, marks


@app.callback(
    [Output('candle-graph', 'figure'),
     Output('sma-graph', 'figure'),
     Output('volume-graph', 'figure'),
     Output('sma-quarter-graph', 'figure'),
     Output('vix-graph', 'figure'),
     Output('regime-graph', 'figure'),
     Output('bollinger-graph', 'figure'),
     Output('stoch-osc-graph', 'figure'),
     Output('rsi-graph', 'figure'),
     Output('macd-graph', 'figure'),
     Output('date-range-div', 'children')],
    [Input('range-slider', 'value'),
     Input('stock-dropdown', 'value')]
    # [Input('sma-graph', 'id')]
)
def update_charts(slider_range, symbol):
    """
    Define the callback to update the 50/200 SMA
    """
    # global df, start_date
    start, end = slider_range
    total_len = len(df)
    if total_len == 0:
        empty_fig = go.Figure()
        return (empty_fig,) * 10 + ("No data available",)
    start = max(0, min(start, total_len - 1))
    end = max(0, min(end, total_len - 1))
    if start > end:
        start, end = end, start

    df_filtered = df.iloc[start:end + 1].copy()

    required_ta_cols = {
        'golden_cross': 0,
        'death_cross': 0,
        'states': np.nan,
        'BollingerUpper': np.nan,
        'BollingerLower': np.nan,
        'BollingerMiddle': np.nan,
        'StochK': np.nan,
        'StochD': np.nan,
        'RSI': np.nan,
        'MACD': np.nan,
        'MACDS': np.nan,
    }
    missing_cols = [col for col in required_ta_cols if col not in df_filtered.columns]
    if missing_cols:
        for col in missing_cols:
            df_filtered[col] = required_ta_cols[col]
        l.warning(f"Missing TA columns for {symbol}: {missing_cols}")

    # 
    # 50/200 sma
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['Close'],
        mode='lines', name='Stock Price',
        line=dict(color='blue')
    ))
    # Add the 50-day SMA line
    fig1.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['50_SMA'],
        mode='lines', name='50-Day SMA',
        line=dict(color='orange')
    ))
    # Add the 200-day SMA line
    fig1.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['200_SMA'],
        mode='lines', name='200-Day SMA',
        line=dict(color='green')
    ))
    
    golden_crosses = df_filtered[df_filtered['golden_cross'] == 1]
    death_crosses = df_filtered[df_filtered['death_cross'] == 1]
    # Add markers for golden crosses
    fig1.add_trace(go.Scatter(
        x=golden_crosses.index, y=golden_crosses['50_SMA'],
        mode='markers', name='Golden Cross',
        marker=dict(color='red', size=15, symbol='star')
    ))
    # Add markers for death crosses
    fig1.add_trace(go.Scatter(
        x=death_crosses.index, y=death_crosses['50_SMA'],
        mode='markers', name='Death Cross',
        marker=dict(color='black', size=15, symbol='x')
    ))
    fig1.update_layout(
        yaxis_title="Price with 50/200-Day SMA",
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(rangeslider=dict(visible=False), tickangle=0),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    #
    # volume chart
    fig111 = go.Figure()
    fig111.add_trace(go.Bar(
        x=df_filtered.index, y=df_filtered['Volume'],
        name='Volume'
        # line=dict(color='blue')
    ))
    fig111.update_layout(
        title=f'Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        # xaxis_rangeslider_visible=True
    )
    # # Add the 50-day SMA line
    # fig111.add_trace(go.Scatter(
    #     x=df_filtered.index, y=df_filtered['50_SMA'],
    #     mode='lines', name='50-Day SMA',
    #     line=dict(color='orange')
    # ))
    # # Add the 200-day SMA line
    # fig111.add_trace(go.Scatter(
    #     x=df_filtered.index, y=df_filtered['200_SMA'],
    #     mode='lines', name='200-Day SMA',
    #     line=dict(color='green')
    # ))
    
    # 
    # sma for quarter 100/50/20
    fig12 = go.Figure()
    fig12.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['Close'],
        mode='lines', name='Stock Price',
        line=dict(color='blue')
    ))
    # Add the 100-day SMA line
    fig12.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['100_SMA'],
        mode='lines', name='100-Day SMA',
        line=dict(color='purple')
    ))
    # Add the 50-day SMA line
    fig12.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['50_SMA'],
        mode='lines', name='50-Day SMA',
        line=dict(color='orange')
    ))
    # Add the 20-day SMA line
    fig12.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['20_SMA'],
        mode='lines', name='20-Day SMA',
        line=dict(color='red')
    ))
    fig12.update_layout(
        yaxis_title="Price with 20/50/100-Day SMA",
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            tickangle=0  # Set the tick angle to 45 degrees
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    # 
    # vix
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_filtered.index, y=df_vix['Close'],
        mode='lines', name='50-Day SMA',
        line=dict(color='red')
    ))
    fig2.update_layout(
        yaxis_title="VIX",
        height=200, 
        xaxis=dict(rangeslider=dict(visible=False), tickangle=0),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    
    # 
    # regime detection 
    # df_filtered['color'] = df_filtered['states'].apply(lambda x: 'red' if x == 0.0 else 'blue')   
    df_filtered['color'] = df_filtered['states'].apply(lambda x: 'red' if x == 0.0 else 'blue')   
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['Close'],
        mode='lines', name='Stock Price',
        line=dict(color='blue')
    ))
    
    # Add markers for regime change
    regime_change = df_filtered[df_filtered['color'] == 'red']
    fig3.add_trace(go.Scatter(
        x=regime_change.index, y=regime_change['Close'],
        mode='markers', name='Regime Change',
        marker=dict(color='red', size=5, symbol='0')
    ))
    fig3.update_layout(
        yaxis_title="Regime Detection",
        height=400, 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(rangeslider=dict(visible=False), tickangle=0),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    
    # 
    # bollinger bands
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['Close'],
        mode='lines', name='Stock Price',
        line=dict(color='blue')
    ))
    fig4.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['BollingerUpper'],
        mode='lines', name='Upper',
        line=dict(color='red')
    ))
    fig4.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['BollingerLower'],
        mode='lines', name='Lower',
        line=dict(color='Green')
    ))
    fig4.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['BollingerMiddle'],
        mode='lines', name='Mid 20',
        line=dict(color='orange')
    ))
    fig4.update_layout(
        yaxis_title="Bollinger Bands",
        height=400,
        xaxis=dict(rangeslider=dict(visible=False), tickangle=0),
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    
    # 
    # stochastic oscillator
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['StochK'],
        mode='lines', name='k',
        line=dict(color='orange')
    ))
    fig6.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['StochD'],
        mode='lines', name='d',
        line=dict(color='blue')
    ))
    fig6.update_layout(
        yaxis_title="Stochastic Oscillator",
        height=300,
        xaxis=dict(
            rangeslider=dict(visible=False),
            tickangle=0  # Set the tick angle to 45 degrees
        ),
        shapes=[
        # Add the same shape in the layout to ensure it's part of the plot
        dict(
            type='rect',
            x0=min(df_filtered.index), x1=max(df_filtered.index),
            y0=80, y1=100, fillcolor='red', opacity=0.1, layer='below'
        ),
        dict(
            type='rect',
            x0=min(df_filtered.index), x1=max(df_filtered.index),
            y0=0, y1=20, fillcolor='green', opacity=0.1, layer='below'
        )
        ],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=20, b=20),
    )

    # 
    # rsi
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['RSI'],
        mode='lines', name='RSI',
        line=dict(color='blue')
    ))
    fig7.update_layout(
        yaxis_title="RSI",
        height=300,
        xaxis=dict(
            rangeslider=dict(visible=False),
            tickangle=0  # Set the tick angle to 45 degrees
        ),
       shapes=[
        # Add the same shape in the layout to ensure it's part of the plot
        dict(
            type='rect',
            x0=min(df_filtered.index), x1=max(df_filtered.index),
            y0=70, y1=100, fillcolor='red', opacity=0.1, layer='below'
        ),
        dict(
            type='rect',
            x0=min(df_filtered.index), x1=max(df_filtered.index),
            y0=0, y1=30, fillcolor='green', opacity=0.1, layer='below'
        )
        ],
        margin=dict(l=20, r=20, t=20, b=20),
    )
    
    # 
    # macd
    fig8 = go.Figure()
    fig8.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['MACD'],
        mode='lines', name='MACD',
        line=dict(color='blue')
    ))
    fig8.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['MACDS'],
        mode='lines', name='Signal',
        line=dict(color='orange')
    ))
    fig8.update_layout(
        yaxis_title="MACD",
        height=200,
        xaxis=dict(rangeslider=dict(visible=False), tickangle=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    
    # candle chart
    # Create a candlestick chart
    fig9 = go.Figure(data=[go.Candlestick(
        x=df_filtered.index,
        open=df_filtered['Open'],
        high=df_filtered['High'],
        low=df_filtered['Low'],
        close=df_filtered['Close']
    )])
    fig9.update_layout(
        yaxis_title="Candle",
        height=600,
        xaxis=dict(rangeslider=dict(visible=False), tickangle=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    # Show the figure
    return fig9, fig1, fig111, fig12, fig2, fig3, fig4, fig6, fig7, fig8, f'{df.index[start].date()} to {df.index[end].date()}'


def min_max_close(df, num_years):
    num_trading_days = 252

    window_size = num_trading_days * num_years 
    period_min = df['Close'].rolling(window=window_size, min_periods=1).min()
    period_max = df['Close'].rolling(window=window_size, min_periods=1).max()
    
    return period_min.iloc[-1], period_max.iloc[-1]


if __name__ == '__main__':    
    app.run(debug=True)
