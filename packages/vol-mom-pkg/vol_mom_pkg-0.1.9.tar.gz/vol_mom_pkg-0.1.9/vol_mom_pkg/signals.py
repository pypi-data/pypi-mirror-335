import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from .data import get_constituents_and_concat, get_ohlc, get_ohlc_alpaca

def calculate_portfolios(lookback, total_portfolio):
    # Load and preprocess data as usual
    end = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=lookback*2)).strftime("%Y-%m-%d")
    universe = get_constituents_and_concat()
    df = get_ohlc_alpaca(universe, start, end)

    df = df.transpose().dropna().transpose()
    df.index = pd.to_datetime([str(x)[:10] for x in df.index])
    df = df.sort_index()

    l_s_ratio = 1/2

    # Strategies
    mom_long_3, mom_short_3, mom_long, mom_short, sorted_mom = get_winners_and_losers(df, lookback, l_s_ratio, total_portfolio)
    vol_long_3, vol_short_3, vol_long, vol_short, sorted_vol = get_vol(df, lookback, l_s_ratio, total_portfolio)


    low_vol_from_winners = double_sorted(mom_long, sorted_vol, 'LONG', 'HVOL')
    high_vol_from_losers = double_sorted(mom_short, sorted_vol, 'SHORT', 'HVOL')
    winners_from_low_vol = double_sorted(vol_long, sorted_mom, 'LONG', 'Momentum {}d'.format(lookback))
    losers_from_high_vol = double_sorted(vol_short, sorted_mom, 'SHORT', 'Momentum {}d'.format(lookback))


    wml = pd.concat([mom_long_3, mom_short_3]).drop(columns="Abs Momentum").reset_index(drop=True)
    lvolhvol = pd.concat([vol_long_3, vol_short_3]).reset_index(drop=True)

    winners_from_low_vol, losers_from_high_vol, low_vol_from_winners, high_vol_from_losers = get_weights_and_allocation(low_vol_from_winners.reset_index(drop=True), high_vol_from_losers.reset_index(drop=True), winners_from_low_vol.reset_index(drop=True), losers_from_high_vol.reset_index(drop=True),total_portfolio, lookback, l_s_ratio)
    
    winners_from_low_vol['Symbol'] = [x.replace("-", '.') for x in winners_from_low_vol["Symbol"]]
    losers_from_high_vol['Symbol'] = [x.replace("-", '.') for x in losers_from_high_vol["Symbol"]]
    low_vol_from_winners['Symbol'] = [x.replace("-", '.') for x in low_vol_from_winners["Symbol"]]
    high_vol_from_losers['Symbol'] = [x.replace("-", '.') for x in high_vol_from_losers["Symbol"]]

    return winners_from_low_vol, losers_from_high_vol, low_vol_from_winners, high_vol_from_losers 



def get_winners_and_losers(df, lookback, l_s_ratio, total_portfolio):
    close_prices = df.xs("Close", level=1, axis=1)
    momentum = close_prices.pct_change()
    momentum = momentum.rolling(window=lookback).sum()
    momentum.index = pd.to_datetime(momentum.index)
    momentum.index = momentum.index.strftime('%Y-%m-%d')

    momentum = momentum.dropna().tail(1).transpose()
    momentum = momentum.rename(columns={momentum.columns[0]: "Momentum {}d".format(lookback)})
    sorted_mom = momentum.sort_values(by="Momentum {}d".format(lookback), ascending=False)
    sorted_mom = sorted_mom.reset_index()
    sorted_mom = sorted_mom.rename(columns={"index":'Symbol'})

    winners_list = sorted_mom.head((len(sorted_mom)//3))
    losers_list = sorted_mom.tail((len(sorted_mom)//3)).sort_values("Momentum {}d".format(lookback), ascending=True)
    long = sorted_mom.head((len(sorted_mom)//2))
    short = sorted_mom.tail((len(sorted_mom)//2)).sort_values("Momentum {}d".format(lookback), ascending=True)
    
    long['Weight'] = long['Momentum {}d'.format(lookback)]/long['Momentum {}d'.format(lookback)].sum()
    short['Abs Momentum'] = short['Momentum {}d'.format(lookback)].abs()
    short['Weight'] = short["Abs Momentum"]/short['Abs Momentum'].sum()
    
    long_portfolio_allocation = total_portfolio * l_s_ratio
    short_portfolio_allocation = total_portfolio * (1-l_s_ratio)
    
    long['Dollar Allocation'] = long['Weight']*long_portfolio_allocation
    short['Dollar Allocation'] = (short['Weight']*short_portfolio_allocation*-1)

    return long, short.reset_index(drop=True), winners_list, losers_list, sorted_mom


        
def get_vol(df, lookback, l_s_ratio, total_portfolio):
    close_prices = df.xs("Close", level=1, axis=1)
    returns = close_prices/close_prices.shift(1)
    returns = returns.dropna()
    returns = returns.apply(np.float64)
    
    returns = returns.apply(np.log)
    std_devs = returns.rolling(window=lookback).std() * np.sqrt(252)
    std_devs = std_devs.dropna().tail(1).transpose()

    std_devs.columns = ['HVOL']
    std_dev_df = std_devs.reset_index()

    std_dev_df = std_dev_df.rename(columns={"index": 'Symbol'})

    std_dev_df_sorted = std_dev_df.sort_values(by='HVOL', ascending=False)

    high_vol_list = std_dev_df_sorted.head(len(std_dev_df_sorted)//3)
    low_vol_list = std_dev_df_sorted.tail(len(std_dev_df_sorted)//3).sort_values("HVOL", ascending=True)
    short = std_dev_df_sorted.head(len(std_dev_df_sorted)//2).reset_index()
    long = std_dev_df_sorted.tail(len(std_dev_df_sorted)//2).sort_values('HVOL', ascending=True).reset_index()
    short['Weight'] = short['HVOL']/short['HVOL'].sum()
    long['Weight'] = long['HVOL']/long['HVOL'].sum()
    
    long_portfolio_allocation = total_portfolio * l_s_ratio
    short_portfolio_allocation = total_portfolio * (1-l_s_ratio)

    long['Dollar Allocation'] = long['Weight']*long_portfolio_allocation
    short['Dollar Allocation'] = short['Weight']*short_portfolio_allocation*-1

    return long.drop(columns='index'), short.drop(columns='index'), low_vol_list, high_vol_list,  std_dev_df_sorted



def double_sorted(small, big, side, datatype):
    if side == "LONG":
        big = big[big["Symbol"].isin(small["Symbol"])]
        if datatype != "HVOL":
            big = big.sort_values(datatype, ascending=False)
        else:
            big = big.sort_values(datatype, ascending=True)
        return big.head((len(big)//2))
    
    elif side == "SHORT":
        big = big[big["Symbol"].isin(small["Symbol"])]
        if datatype != "HVOL":
            big = big.sort_values(datatype, ascending=True)
        else:
            big = big.sort_values(datatype, ascending=False)
        return big.head((len(big)//2))



def get_weights_and_allocation(st1, st2, mom1, mom2, total_portfolio, lookback, ls_ratio):
    st1["Weight"] = (abs(st1["HVOL"]-1))/st1["HVOL"].sum()
    st1['Dollar Allocation'] = st1['Weight']*total_portfolio
    
    st2["Weight"] = st2["HVOL"]/st2["HVOL"].sum()
    st2['Dollar Allocation'] = st2['Weight']*total_portfolio
    mom1 = mom1[mom1["Momentum {}d".format(lookback)]>=0]

    
    mom1['Abs Momentum'] = mom1['Momentum {}d'.format(lookback)].abs()
    mom1['Weight'] = mom1["Abs Momentum"]/mom1['Abs Momentum'].sum()
    mom1['Dollar Allocation'] = mom1['Weight']*total_portfolio

    mom2 = mom2[mom2["Momentum {}d".format(lookback)]<0]
    mom2['Abs Momentum'] = mom2['Momentum {}d'.format(lookback)].abs()
    mom2['Weight'] = mom2["Abs Momentum"]/mom2['Abs Momentum'].sum()
    mom2['Dollar Allocation'] = mom2['Weight']*total_portfolio


    return st1, st2, mom1, mom2