"""
Pairs Trading Backtest & Parameter Optimization

The strategy operates by computing the spread between two assets, then applying a trading algorithm based on a rolling z-score of that spread. 
Specifically:
- A rolling mean and standard deviation are calculated over a moving window of fixed length (e.g., 50 periods).
- Trading signals are triggered when the z-score exceeds a configurable entry threshold (positive or negative).
- Positions are closed when the spread mean-reverts beyond an exit threshold or hits a defined stop loss.
- The strategy is backtested over a fixed number of past bars (e.g., 5000), which you can customize.
An exhaustive grid search is then performed to evaluate various combinations of parameters

The goal is to identify promising parameter sets under a simple rule-based logic, serving as a baseline framework for more advanced strategy development.

The primary purpose of this code is educational — to explore quantitative trading logic, data manipulation, and optimization routines using Python. 
I can’t guarantee any of this makes sense — it’s more instinct than science!

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
from plotly.express.trendline_functions import rolling
from tqdm import tqdm


mt5.initialize(login=, server="", password="")

def get_data(symbols, interval, n_bars=5000):
    list_data = {}
    for sym in symbols:
        rates = mt5.copy_rates_from(sym, interval, datetime.now(), n_bars)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        list_data[sym] = df['close'].pct_change().dropna()
    return pd.DataFrame(list_data)

symbols = ['USTEC', 'US500']
interval = mt5.TIMEFRAME_M15
data = get_data(symbols=symbols, interval=interval)


def pairs_trading_algo(df, threshold_entry, threshold_exit, stop_loss, window):
    spread = df['USTEC'] - df['US500']
    mean = spread.rolling(window=window).mean()
    stdev = spread.rolling(window=window).std()
    z_score = (spread - mean) / stdev

    position = None
    final_return = 1
    pnl = 1
    nb_trades = 0
    winning_trades = 0

    for i in range(window, len(z_score)):
        current_z = z_score.iloc[i]
        current_spread = spread.iloc[i]

        if position is None:
            if current_z > threshold_entry:
                position = 'short'
                nb_trades += 1
            elif current_z < -threshold_entry:
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
    z_entry = np.arange(0.25,2,0.25)
    exit_rate = np.arange(0.001, 0.008, 0.001)
    stoploss_rate = np.arange(0.001, 0.008, 0.001)

    results = []

    for z in tqdm(z_entry, desc="Optimizing"):
        for exit in exit_rate:
            for sl in stoploss_rate:
                final_return, win_rate, return_per_trade, nb_trades = pairs_trading_algo(data,z, exit, sl,50)
                results.append({
                    'Entry - z': z,
                    'Exit Threshold': exit,
                    'Stop Loss': sl,
                    'Final Return': final_return,
                    'Nb Trades': nb_trades,
                    'Win Rate': win_rate,
                    'Win per Trade': return_per_trade
                })
    df_results = pd.DataFrame(results)

    df_results = df_results[df_results['Nb Trades'] > 10]  # Require minimum trades
    df_results = df_results[df_results['Final Return'] > 0]  # Only positive returns

    df_results.sort_values(by='Final Return', ascending=False, inplace=True)
    top_10 = df_results.head(10)

    print("\nTop 10 Best Combinations:")
    print(top_10.to_string(index=False, float_format="%.3f"))


optimization(data)


# Reminder: Live as if u were to die tomorrow. Learn as if u were to live forever!
