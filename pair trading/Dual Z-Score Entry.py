"""
This script is a new and enhanced version of the "Baseline" code witch you can find in the same directory.
It builds upon the original strategy by introducing two Z-scores instead of one, each computed with a different rolling window length:
- one short-term
- one long-term.
The entry logic now uses two complementary Z-score thresholds, providing more nuanced trade signals compared to the original baseline.
The additional Z-score significantly increased computation time, so the console output was adjusted for clearer progress tracking.

⚠️ Disclaimer:
This project is NOT financial advice and is NOT intended for live trading. It is provided purely
for educational and research purposes. Use it at your own risk. Always consult with a financial professional
before making investment decisions.

Author: Anthony Gocmen
"""


import time
from itertools import count
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from plotly.express.trendline_functions import rolling
from tqdm import tqdm

if not mt5.initialize(login=, server="", password=""):
    raise ConnectionError(f"[ERROR] Cannot connect to MT5 - {mt5.last_error()}")


def get_data(symbols, interval, n_bars=5000):
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
        list_data[sym] = df['close'].pct_change().dropna()

    return pd.DataFrame(list_data)

symbols = ['US30', 'US500']
interval = mt5.TIMEFRAME_M15
data = get_data(symbols=symbols, interval=interval, n_bars=5000)


def pairs_trading_algo(df, z_entry_near, z_entry_far, threshold_exit, stop_loss, window_near, window_far):
    spread = df['US30'] - df['US500']
    mean_near = spread.rolling(window=window_near).mean()
    stdev_near = spread.rolling(window=window_near).std()
    mean_far = spread.rolling(window=window_far).mean()
    stdev_far = spread.rolling(window=window_far).std()
    z_score_near = (spread - mean_near) / stdev_near
    z_score_far = (spread - mean_far) / stdev_far

    position = None
    final_return = 1
    pnl = 1
    nb_trades = 0
    winning_trades = 0

    for i in range(window_far, len(z_score_far)):
        current_z_near = z_score_near.iloc[i]
        current_z_far = z_score_far.iloc[i]
        current_spread = spread.iloc[i]

        if position is None:
            if current_z_near > z_entry_near and current_z_far > z_entry_far:
                position = 'short'
                nb_trades += 1
            elif current_z_near < -z_entry_near and current_z_far < -z_entry_far:
                position = 'long'
                nb_trades += 1

        elif position == 'long':
            pnl *= 1 + current_spread
            if pnl - 1 >= threshold_exit or pnl - 1 <= -stop_loss:
                final_return *= pnl
                if pnl - 1 > 0: winning_trades += 1
                position = None
                pnl = 1

        elif position == 'short':
            pnl *= 1 - current_spread
            if pnl - 1 >= threshold_exit or pnl - 1 <= -stop_loss:
                final_return *= pnl
                if pnl - 1 > 0: winning_trades += 1
                position = None
                pnl = 1


    win_rate = (winning_trades / nb_trades) * 100 if nb_trades > 0 else 0
    return_per_trade = ((final_return-1) / nb_trades) * 100
    final_return = (final_return - 1) * 100

    return final_return, win_rate, return_per_trade, nb_trades


def optimization (data):
    z_entry = np.arange(0.2,1.3,0.2)
    z_entry_far = np.arange(0.2,1.3,0.2)
    exit_rate = np.arange(0.001, 0.008, 0.002)
    stoploss_rate = np.arange(0.001, 0.008, 0.002)
    short_window = range(10, 50, 5)
    large_window = range(150, 400, 50)

    results = []
    z_done = 0

    for z_near in z_entry:
        z_done += 1
        print(f"====== Computing {z_done}/{len(z_entry)} ======")
        time.sleep(0.2)
        for z_far in tqdm(z_entry_far, desc="Optimizing"):
            for exit in exit_rate:
                for sl in stoploss_rate:
                    for short_count in short_window:
                        for large_count in large_window:
                            final_return, win_rate, return_per_trade, nb_trades = pairs_trading_algo(data, z_near, z_far, exit, sl, short_count, large_count)
                            results.append({
                                'Entry - z Near': z_near,
                                'Entry - z Far': z_far,
                                'Exit Threshold': exit,
                                'Stop Loss': sl,
                                'Window - Near': short_count,
                                'Window - Far': large_count,
                                'Final Return': final_return,
                                'Nb Trades': nb_trades,
                                'Win Rate': win_rate,
                                'Win per Trade': return_per_trade
                            })
    df_results = pd.DataFrame(results)

    df_results = df_results[df_results['Nb Trades'] > 10]
    df_results = df_results[df_results['Win per Trade'] > 0.1]
    df_results = df_results[df_results['Final Return'] > 0]

    df_results.sort_values(by='Final Return', ascending=False, inplace=True)
    top_10 = df_results.head(10)

    print("\nTop 10 Best Combinations:")
    print(top_10.to_string(index=False, float_format="%.3f"))


optimization(data)
