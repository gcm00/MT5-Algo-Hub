"""
Get Market Depth (Market Book) from MetaTrader 5 (MT5) in Python.

This script connects to a MetaTrader 5 account and retrieves the live market depth (order book)
for a specified symbol (default: "EURUSD"). The output includes bid and ask levels with associated volumes.

Setup Instructions:
- You must manually open the Market Depth (order book) window on the MT5 terminal for the symbol you're targeting (e.g., EURUSD).
- Replace the blank login credentials below with your own demo or live MT5 account details.
- Make sure MetaTrader 5 is installed and that the Python-MT5 API is working properly.

⚠️ Disclaimer:
This project is NOT financial advice and is NOT intended for live trading. It is provided purely
for educational and research purposes. Use it at your own risk. Always consult with a financial professional
before making investment decisions.

Author: Anthony Gocmen
"""

import MetaTrader5 as mt5
import pandas as pd

# Initialize MetaTrader5
if not mt5.initialize(login=, server="", password=""):
    print("Initialization failed. Error code:", mt5.last_error())
    mt5.shutdown()
    quit()

# Try to subscribe to the Market Book
if mt5.market_book_add("EURUSD"):
    book = mt5.market_book_get("EURUSD")
    if book is not None:
        # Parse book data into a DataFrame
        book_list = [{
            "type": 'bid' if item.type == mt5.BOOK_TYPE_BUY else 'ask',
            "price": item.price,
            "volume": item.volume
        } for item in book]

        df = pd.DataFrame(book_list)
        print(df.to_string(index=False))
    else:
        print("Failed to retrieve Market Book data.")

    # Release the Market Book
    mt5.market_book_release("EURUSD")
else:
    print("Failed to activate Market Book.")

# Shutdown MetaTrader5
mt5.shutdown()
