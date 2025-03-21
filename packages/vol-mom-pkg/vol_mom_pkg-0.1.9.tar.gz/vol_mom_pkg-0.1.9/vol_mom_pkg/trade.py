from alpaca_trade_api.rest import REST, TimeFrame
from vol_mom_pkg.signals import calculate_portfolios
import pandas as pd
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
api = REST(ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_BASE_URL)

def get_account_info():
    account = api.get_account()
    return float(account.equity)  # Equivalent to Net Liquidation

def place_orders(df, trade_direction):
    def adjust_position(symbol, target_allocation):
        try:
            # Fetch previous close price
            bars = api.get_bars(symbol, TimeFrame.Day, limit=5).df
            if bars.empty:
                print(f"Skipping {symbol}, no price data available.")
                return

            previous_close = bars.iloc[-1].close
            target_shares = int(target_allocation // previous_close)  # Desired shares to hold

            # Check if we already own the stock
            try:
                position = api.get_position(symbol)  # Fetch current holdings
                current_shares = int(float(position.qty))  # Convert to integer
            except Exception:
                current_shares = 0  # If no position, assume 0

            share_diff = target_shares - current_shares  # Net change needed

            if share_diff > 0:
                # Need to buy more shares
                api.submit_order(
                    symbol=symbol,
                    qty=share_diff,
                    side="buy",
                    type="market",
                    time_in_force="gtc"
                )
                print(f"BUY {share_diff} shares of {symbol} to reach target {target_shares}.")
            elif share_diff < 0:
                # Need to sell excess shares
                api.submit_order(
                    symbol=symbol,
                    qty=abs(share_diff),
                    side="sell",
                    type="market",
                    time_in_force="gtc"
                )
                print(f"SELL {abs(share_diff)} shares of {symbol} to reach target {target_shares}.")
            else:
                print(f"{symbol} is already at the target allocation ({target_shares} shares). No action needed.")

        except Exception as e:
            print(f"Error adjusting position for {symbol}: {e}")

    for _, row in df.iterrows():
        adjust_position(row["Symbol"], row["Dollar Allocation"])

def close_positions(new_portfolio_df):
    try:
        # Get all currently held positions
        positions = api.list_positions()
        new_portfolio_symbols = set(new_portfolio_df["Symbol"])  # Stocks in new portfolio

        for position in positions:
            symbol = position.symbol

            # If stock is not in the new portfolio, close it
            if symbol not in new_portfolio_symbols:
                qty = abs(int(float(position.qty)))  # Ensure quantity is positive
                side = "sell" if position.side == "long" else "buy"

                api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type="market",
                    time_in_force="gtc"
                )
                print(f"Closing {side.upper()} order for {qty} shares of {symbol} (not in new portfolio).")

        print("Unwanted positions have been closed.")
    except Exception as e:
        print(f"Error closing positions: {e}")



def send_weekly_basket():
    pf = get_account_info()
    lookback = 22
    winners_from_low_vol, losers_from_high_vol, low_vol_from_winners, high_vol_from_losers = calculate_portfolios(lookback, pf)
    close_positions(losers_from_high_vol)
    place_orders(losers_from_high_vol, 'long')

