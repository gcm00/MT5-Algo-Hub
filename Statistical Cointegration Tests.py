"""
This script performs statistical tests to evaluate potential pairs trading opportunities between
two financial instruments (default: US30 and US500).

This code:
1. Performs Augmented Dickey-Fuller (ADF) tests on:
  * Simple price difference (Asset1 - Asset2)           => NAIVE, assumes the assets are perfectly 1:1 related
  * Price ratio (Asset1 / Asset2)                       => NAIVE, also assumes a fixed relationship, but multiplicative
2. Conducts formal cointegration test (Engle-Granger)   => ROBUST, testing whether the residuals ε are stationary

⚠️ Disclaimer:
This project is NOT financial advice and is NOT intended for live trading. It is provided purely
for educational and research purposes. Use it at your own risk. Always consult with a financial professional
before making investment decisions.

Author: Anthony Gocmen
"""


import MetaTrader5 as mt5
import pandas as pd
import statsmodels.api as sm
from datetime import datetime
from statsmodels.tsa.stattools import adfuller, coint


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
    return pd.DataFrame(list_data).dropna()


def find_adf(data):
    asset1 = data.iloc[:, 0]
    asset2 = data.iloc[:, 1]

    print("Testing Cointegration according to:")

    print("--------- Spread Difference ---------")
    spread_diff = asset1 - asset2
    adf_spread_diff = adfuller(spread_diff)
    print(f"ADF p-value: {adf_spread_diff[1]:.4f} \n")

    print("--------- Spread Ratio ---------")
    spread_ratio = asset1 / asset2
    adf_spread_ratio = adfuller(spread_ratio)
    print(f"ADF p-value on spread: {adf_spread_ratio[1]:.4f} \n")

    print("--------- Engle-Granger ---------")
    coint_result = coint(asset1, asset2)
    print(f"Cointégration p-value : {coint_result[1]:.4f}")


# ------------ Parameters ------------
tickers = ['US30','US500']
timeframe = mt5.TIMEFRAME_M15
count = 20000


# ------------ Execution ------------
data = get_data(tickers=tickers, timeframe=timeframe, nb_bars=count)
find_adf(data)

