import dash
from dash import dcc, html
import plotly.graph_objs as go
import yfinance as yf
import numpy as np


# Fetch AAPL stock data
def fetch_data(ticker):
    data = yf.download(ticker, start="2020-01-01", end="2023-12-31")
    return data


# Calculate SMAs and generate signals
def calculate_sma(data, short_window, long_window):
    # Calculate SMA_short and SMA_long
    data['SMA_short'] = data['Adj Close'].rolling(window=short_window, min_periods=1).mean()
    data['SMA_long'] = data['Adj Close'].rolling(window=long_window, min_periods=1).mean()

    # Initialize Signal column
    data['Signal'] = 0

    # Calculate signals based on SMA_short and SMA_long
    data.loc[data.index[short_window:], 'Signal'] = np.where(data['SMA_short'][short_window:] > data['SMA_long'][short_window:], 1, 0)

    # Calculate Position column
    data['Position'] = data['Signal'].diff()

    return data


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Fetch data and calculate SMAs
data = fetch_data('AAPL')
data = calculate_sma(data, short_window=40, long_window=100)

# Layout of the Dash app
app.layout = html.Div(children=[
    html.H1(children='AAPL Stock Backtesting using SMA'),

    dcc.Graph(
        id='stock-chart',
        figure={
            'data': [
                go.Scatter(
                    x=data.index,
                    y=data['Adj Close'],
                    mode='lines',
                    name='AAPL Adj Close'
                ),
                go.Scatter(
                    x=data.index,
                    y=data['SMA_short'],
                    mode='lines',
                    name='40-day SMA'
                ),
                go.Scatter(
                    x=data.index,
                    y=data['SMA_long'],
                    mode='lines',
                    name='100-day SMA'
                ),
                go.Scatter(
                    x=data[data['Position'] == 1].index,
                    y=data['SMA_short'][data['Position'] == 1],
                    mode='markers',
                    name='Buy Signal',
                    marker=dict(symbol='triangle-up', color='green', size=10)
                ),
                go.Scatter(
                    x=data[data['Position'] == -1].index,
                    y=data['SMA_short'][data['Position'] == -1],
                    mode='markers',
                    name='Sell Signal',
                    marker=dict(symbol='triangle-down', color='red', size=10)
                )
            ],
            'layout': go.Layout(
                title='AAPL Stock Price with 40-day and 100-day SMA',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Price'},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=False)
