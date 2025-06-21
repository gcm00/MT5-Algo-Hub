"""
This script is an extended version of the 'Baseline' script that originally involved only two assets.
This updated version explores a tri-asset approach using MetaTrader 5 data.

⚠️ Disclaimer:
This project is NOT financial advice and is NOT intended for live trading. It is provided purely
for educational and research purposes. Use it at your own risk. Always consult with a financial professional
before making investment decisions.

Author: Anthony Gocmen
"""


from itertools import count
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openpyxl.styles.builtins import neutral
from plotly.express.trendline_functions import rolling
from pygments.lexers.sql import sqlite_prompt_re
from tqdm import tqdm


if not mt5.initialize(login=, server="", password=""):
    raise ConnectionError(f"[ERROR] Cannot connect to MT5 - {mt5.last_error()}")

def get_data(symbols, interval, n_bars=10000):
    list_data = {}
    for sym in symbols:
        if not mt5.symbol_select(sym, True):
            raise ValueError(f'[Error] - Selection of the Ticker {sym} - {mt5.last_error()}')
        rates = mt5.copy_rates_from(sym, interval, datetime.now(), n_bars)
        if rates is None or len(rates) == 0:
            raise ValueError(f'[Error] - Get data from {sym}')
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        list_data[sym] = df['close'].pct_change()

    return pd.DataFrame(list_data).dropna()

symbols = ['', '', '']
interval = mt5.TIMEFRAME_M15
data = get_data(symbols=symbols, interval=interval, n_bars=5000)


def pairs_trading_algo(df, threshold_exit, stop_loss, ratio=3):
    position = None
    final_return = 1
    pnl = 1
    nb_trades = 0
    bought = ""
    sold = ""
    winning_trades = 0
    threshold_exit = threshold_exit / 100
    stop_loss = stop_loss / 100

    asset1, asset2, asset3 = df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2]

    for i in range(len(df)):
        values = {
            'Asset 1': asset1.iloc[i],
            'Asset 2': asset2.iloc[i],
            'Asset 3': asset3.iloc[i]
        }
        highest_asset, lowest_asset = max(values,key=values.get), min(values, key=values.get)
        neutral_asset = [key for key in values if key != highest_asset and key != lowest_asset][0]

        highest_value, lowest_value, neutral_value = values[highest_asset], values[lowest_asset], values[neutral_asset]
        range_high_low = abs(highest_value - lowest_value)
        range_high_neutral = abs(highest_value - neutral_value)
        range_neutral_low = abs(neutral_value - lowest_value)

        if position is None:
            if range_high_neutral >= range_high_low/ratio and range_neutral_low >= range_high_low/ratio:
                position = "Open"
                nb_trades += 1
                bought = lowest_asset
                sold = highest_asset

        elif position == "Open":
            spread = values[bought] - values[sold]
            pnl *= 1 + spread
            if pnl - 1 >= threshold_exit or pnl - 1 <= -stop_loss:
                final_return *= pnl
                if pnl - 1 > 0: winning_trades += 1
                position = None
                pnl = 1

    win_rate = (winning_trades / nb_trades) * 100 if nb_trades > 0 else 0
    return_per_trade = ((final_return-1) / nb_trades) * 100 if nb_trades > 0 else 0
    final_return = (final_return - 1) * 100

    return final_return, win_rate, return_per_trade, nb_trades


def optimization (data):
    exit_rate = np.arange(0.08, 0.25, 0.03)
    stoploss_rate = np.arange(0.05, 0.8, 0.05)
    ratio = np.arange(2.8,3.1,0.2)
    results = []

    for exit in tqdm(exit_rate, desc="Optimizing"):
            for sl in stoploss_rate:
                for x in ratio:
                    final_return, win_rate, return_per_trade, nb_trades = pairs_trading_algo(data,exit, sl, x)
                    results.append({
                        'Exit Threshold': exit,
                        'Stop Loss': sl,
                        'Ratio': x,
                        'Final Return': final_return,
                        'Nb Trades': nb_trades,
                        'Win Rate': win_rate,
                        'Win per Trade': return_per_trade
                    })
    df_results = pd.DataFrame(results)

    df_results.sort_values(by='Win per Trade', ascending=False, inplace=True)
    top_10 = df_results.head(40)

    print("\nTop 10 Best Combinations:")
    print(top_10.to_string(index=False, float_format="%.2f"))

optimization(data)

