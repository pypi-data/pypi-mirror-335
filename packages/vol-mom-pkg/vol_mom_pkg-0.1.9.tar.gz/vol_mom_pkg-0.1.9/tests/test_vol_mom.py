import pandas as pd
from volmompkg.vol_mom_pkg.trade import send_weekly_basket
from volmompkg.vol_mom_pkg.broker_info import get_incremental_pnl, get_orders, get_positions, get_account, get_daily_pnl, get_transactions, get_historical_pnl


if __name__ == "__main__":
    # send_weekly_basket()
    # exit()
    # print(get_orders())
    # print(get_positions())
    # print(get_account())
    # print(get_daily_pnl())
    # print(get_transactions())
    # print(get_historical_pnl())
    print(get_incremental_pnl("2025-02-01", "2025-03-19"))
