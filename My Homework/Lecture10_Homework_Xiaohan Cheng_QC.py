# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 17:05:53 2021

@author: Xiaohan Cheng
"""

# Write a Pairs Trading Strategy that trades on a portfolio of two pairs of stocks GS vs. MS, and AAPL vs MSFT, 
# based on the log difference in prices and the following parameters:

# 1. Parameters: entry point = 1, exit point = 0. Hedge ratio is based on the slopoe of the linear regression using the rolling 90-day lookback period
# 2. Implement the strategy in QuantConnect, and backtest it:
#    Backtest our strategy using three 3-month periods: Feb 1 - May 1 in 2018, 2019 and 2020.
#    Trading Frequency: Daily
#    What can you do on exit or entry point to iprove the backtesting PnL performance? Articulate the trade-offs between profitability and risk using high or low entry/exit points.
#    For example, what are the pros and cons for increasing the entry point from 1 to 2?
#       High entry point might improve the PnL performance but also improve the risk.
#    What can you do to decrease the drawdown risk?
#       use a stoploss line

import math
import numpy as np
import pandas as pd
from scipy import stats

class Lecture10Homework(QCAlgorithm):

    def Initialize(self):

    
        #self.SetStartDate(2018, 2, 1)  
        #self.SetEndDate(2018, 5, 1)
        #self.SetStartDate(2019, 2, 1)  
        #self.SetEndDate(2019, 5, 1)        
        self.SetStartDate(2020, 2, 1)  
        self.SetEndDate(2020, 5, 1)       
        
        
        
        self.SetCash(100000) 
        
        
        self.gs = self.AddEquity("GS", Resolution.Daily)
        self.ms = self.AddEquity("MS", Resolution.Daily)
        self.aapl = self.AddEquity("AAPL", Resolution.Daily)
        self.msft = self.AddEquity("MSFT", Resolution.Daily)
        
        
        # trades every day
        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.AfterMarketOpen("GS"), self.Strategy)
       
        
    def Strategy(self):
        # Another way to write
        # tickers = ["GS", "MS", "AAPL", "MSFT"]
        # symbols = [qb.AddEquity(ticker, Resolution.Daily).Symbol for ticker in tickers]
  
        df = self.History(self.Securities.Keys, 90, Resolution.Daily)
        
        df1 = df.loc["GS"]
        df2 = df.loc["MS"]
        df3 = df.loc["AAPL"]
        df4 = df.loc["MSFT"]
        
        df1['log'] = df1['close'].apply(lambda x: math.log(x))
        df2['log'] = df2['close'].apply(lambda x: math.log(x))
        df3['log'] = df3['close'].apply(lambda x: math.log(x))
        df4['log'] = df4['close'].apply(lambda x: math.log(x))
       
        df1['log_diff'] = df1['log'] - df2['log']
        df3['log_diff'] = df3['log'] - df4['log']
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(df2['log'],df1['log'])
        Wp = 1/(1+slope) # weight of asset P
        Wq = 1-Wp        # weight of asset Q
        
        
        df1['W'] = df1['log'] - slope * df2['log']
        
        sigma = np.std(df1['W'])
        mu = df1['W'].mean()
        df1['μ+σ'] = mu + sigma
        df1['μ-σ'] = mu - sigma
        
        
        if not self.Portfolio.Invested:        # Enter
            # When W > μ+σ, buy Q and sell P
            if df1['W'][-2] > df1['μ+σ'][-2]:
                self.SetHoldings("GS", -Wp)
                self.SetHoldings("MS", Wq)
            # When W < μ-σ, buy P and sell Q
            if df1['W'][-2] < df1['μ-σ'][-2]:
                self.SetHoldings("GS", Wp)
                self.SetHoldings("MS", -Wq)
        elif abs(df1['W'][-2] - mu) < 0.01:     # Exit When W = μ, Liquidate all the positions
            self.Liquidate("GS")
            self.Liquidate("MS")
            
    def OnData(self, data):
        self.Strategy