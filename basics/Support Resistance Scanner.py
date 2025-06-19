"""
⚠️ Disclaimer:
This project is NOT financial advice and is NOT intended for live trading. It is provided purely
for educational and research purposes. Use it at your own risk. Always consult with a financial professional
before making investment decisions.

Author: Anthony Gocmen
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import Counter

# Fill the following line with ur infos
mt5.initialize(login=, server="", password="")


def analyze_highs_lows():
    # Initialize Parameters
    SYMBOL = "The Ticker U Want"
    timeframe = mt5.TIMEFRAME_M5    # 5-minute candles (MT5_TIMEFRAME_M1, M5, M15, M30, H1, H4, D1, W1)
    rounding_digits = 2             # Better to keep 2 digits but U can change

    # Fetch data
    rates = mt5.copy_rates_from(SYMBOL, timeframe, datetime.now(), 10000)
    df = pd.DataFrame(rates, columns=['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume'])
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Round prices
    df['rounded_high'] = df['high'].round(rounding_digits)
    df['rounded_low'] = df['low'].round(rounding_digits)
    df['rounded_close'] = df['close'].round(rounding_digits)

    # Count price level occurrences
    all_counter = Counter(df['rounded_high']) + Counter(df['rounded_low']) + Counter(df['rounded_close'])
    high_counter = Counter(df['rounded_high'])
    low_counter = Counter(df['rounded_low'])
    close_counter = Counter(df['rounded_close'])

    top_5_highs = high_counter.most_common(5)
    top_5_lows = low_counter.most_common(5)
    top_5_close = close_counter.most_common(5)
    top_10 =  all_counter.most_common(10)

    print("\nTop 5 frequent highs:")
    for level, count in top_5_highs:
        print(f"Price: {level}, Occurrence: {count}")

    print("\nTop 5 frequent lows:")
    for level, count in top_5_lows:
        print(f"Price: {level}, Occurrence: {count}")

    print("\nTop 5 frequent closes:")
    for level, count in top_5_close:
        print(f"Price: {level}, Occurrence: {count}")

    print("\nTop 10 - cumulated:")
    for level, count in top_10:
        print(f"Price: {level}, Occurrence: {count}")


analyze_highs_lows()
mt5.shutdown()

