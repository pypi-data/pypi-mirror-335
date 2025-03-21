import pandas as pd
import yfinance as yf
import alpaca_trade_api as tradeapi
# import os
# from dotenv import load_dotenv
# load_dotenv()
# ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
# ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
# ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL")

ALPACA_API_KEY = "PKSWP8A9QH87I5DX69Y4"
ALPACA_API_SECRET = "we0Fo1a7UmijE45Z3rWYkZjXqnsfFg3B8pwrnbdC"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"


# Initialize Alpaca API client
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_BASE_URL)

def get_constituents_and_concat():
    sp500 = 'https://yfiua.github.io/index-constituents/constituents-sp500.csv'

    sp500 = pd.read_csv(sp500)
    sp500 = sp500.sort_values("Symbol", ascending=True)
    sp500_constituents = sp500['Symbol'].to_list()
    sp500_constituents = [x.replace("-",".") for x in sp500_constituents]

    return sp500_constituents

def get_ohlc(symbols, start_date, end_date):
    data = {}
    for symbol in symbols:
        print(symbol)
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        data[symbol] = df[['Close']]
    
    # Combine the data into a single DataFrame with multi-level columns
    combined_df = pd.concat(data, axis=1)
    return combined_df

def get_ohlc_alpaca(symbols, start_date, end_date):
    barset = api.get_bars(symbols, timeframe="1Day", start=start_date, end=end_date).df

    # Pivot the DataFrame to have symbols as the first level of columns
    barset = barset.pivot_table(values="close", index=barset.index.get_level_values("timestamp"), columns="symbol")
    barset.columns = pd.MultiIndex.from_product([barset.columns, ["Close"]])
    barset = barset.rename_axis(columns=["Symbol", None])
    barset.index = pd.to_datetime(barset.index).date
    return barset