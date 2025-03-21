# **vol-mom-pkg** 

**vol-mom-pkg** is a Python package designed for momentum-based trading strategies that focus on volatility. It calculates portfolios based on historical volatility trends and executes trades using the Alpaca Markets API.

## **Features**
- **Portfolio Signal Calculation**: Identifies winners and losers based on historical volatility.
- **Account Info Retrieval**: Fetches account balance from Alpaca.
- **Trade Execution**: Places market orders based on generated signals.
- **Order Management**: Retrieve past and active orders.
- **Portfolio Monitoring**: Check positions and transaction history.
- **PnL Tracking**: Monitor daily and historical profit and loss (PnL).
- **Stock Screening**: Identify stocks based on custom criteria.
- **Sector Allocation Analysis**: Analyze sector-based portfolio allocation.

---

## **Installation**
Before using the package, install the required dependencies:

```bash
pip install -r requirements.txt
```

Clone the repository (if applicable):

```bash
pip install vol-mom-pkg==0.1.4
```

---

## **Usage**
### **1. Import the necessary functions**
```python
from vol_mom_pkg.trade import send_weekly_basket
from vol_mom_pkg.broker_info import get_orders, get_positions, get_account, get_daily_pnl, get_historical_pnl, get_transactions
```

### **2. Fetch Account Info**
Retrieve your account’s total portfolio value from Alpaca:
```python
account_info = get_account()
```

### **3. Fetch Orders**
Retrieve all past and active orders:
```python
orders = get_orders()
```

### **4. Fetch Portfolio Positions**
Retrieve all active positions in the portfolio:
```python
positions = get_positions()
```

### **5. Fetch Transactions**
Retrieve past transaction history (e.g., fills, dividends, etc.):
```python
transactions = get_transactions()
```

### **6. Track PnL**
#### **Daily PnL**
```python
daily_pnl = get_daily_pnl()
```

#### **7. Historical PnL**
Fetch profit and loss over a custom period:
```python
historical_pnl = get_historical_pnl() # default: last 7 days
historical_pnl = get_historical_pnl(start_date='2023-01-01', end_date='2023-12-31', timeframe='1D')
```

#### **8. Historical PnL**
Df of pnl day to day over a period. 
```python
df = get_incremental_pnl() # default: last 7 days
df = get_incremental_pnl(start_date='2023-01-01', end_date='2023-12-31', timeframe='1D')
```

#### **9. Portfolio Rebalancing**
Rebalance current positions and send in orders for new postions
```python
send_weekly_basket()
```
Output
------------------
```pythonClosing SELL order for 442 shares of WBA (not in new portfolio).
Closing SELL order for 40 shares of WDC (not in new portfolio).
Closing SELL order for 62 shares of WMB (not in new portfolio).
...
BUY 347 shares of FMC to reach target 347.
BUY 61 shares of MRNA to reach target 285.
SELL 6 shares of NVDA to reach target 56.
BUY 41 shares of DECK to reach target 41.
```

## **Configuration**
This package requires Alpaca API credentials. Set them as environment variables:
```python
ALPACA_API_KEY = "your_api_key"
ALPACA_API_SECRET = "your_api_secret"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Use live URL for real trading
```


## **Dependencies**
- `alpaca-trade-api`
- `pandas`
- `numpy`
- `yfinance`
- `setuptools`

