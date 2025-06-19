"""
This script connects to the MT5 trading platform to retrieve historical price data for a given financial instrument (e.g., 'US500').
It then applies the Augmented Dickey-Fuller (ADF) test to assess whether the time series of closing prices is stationary.

Stationarity is a key assumption in many time series models. If a series is stationary,
it means its statistical properties such as mean, variance, and autocorrelation are constant over time.

⚠️ Disclaimer:
This project is NOT financial advice and is NOT intended for live trading. It is provided purely
for educational and research purposes. Use it at your own risk. Always consult with a financial professional
before making investment decisions.

Author: Anthony Gocmen
"""

import MetaTrader5 as mt5
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from datetime import datetime


if not mt5.initialize(login=, server="", password=""):
    raise ConnectionError(f"[ERROR] Cannot connect to MT5 - {mt5.last_error()}")


def get_data(tickers, timeframe, nb_bars):
    list_data = {}
    for ticker in tickers:
        if not mt5.symbol_select(ticker,True):
            raise ValueError(f"[ERROR] Cannot select {ticker} in MT5 - {mt5.last_error()}")
        raw = mt5.copy_rates_from(ticker, timeframe, datetime.now(), nb_bars)
        if raw is None or len(raw) == 0:
            raise ValueError(f"[ERROR] No data returned for {ticker}")
        raw = pd.DataFrame(raw)
        raw['time'] = pd.to_datetime(raw['time'],unit='s')
        raw.set_index('time', inplace=True)
        list_data[ticker] = raw['close']
    return pd.DataFrame(list_data)

def find_adf(data):
    adf = adfuller(data)
    print(f"[ADF] Statistic: {adf[0]:.3f}")
    print(f"[ADF] p-value: {adf[1]:.3f}")


# ------------ Parameters ------------
tickers = ['US500']
timeframe = mt5.TIMEFRAME_H1
count = 1000

# ------------ Execution ------------
data = get_data(tickers=tickers, timeframe=timeframe, nb_bars=count)
find_adf(data)
