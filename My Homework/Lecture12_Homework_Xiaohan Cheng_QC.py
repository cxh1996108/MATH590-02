# The answer is in research.ipynb

# Write a Pairs Trading Strategy that trades on a portfolio of two pairs of stocks GS vs. MS, and AAPL vs MSFT, 
# based on the log difference in prices and the following parameters:

# 1. Start with $200,000 cash capital. Margin requirement is 50% on both long and short market values.
# 2. Backtest the Pairs Trading Strategy on QC that you developed in Lecture 10 assignment from 2/1/2020 to 5/1/2020.
# 3. For each day of the backtesting period, compute the daily VaR at 95%.
# 4. If you impose a limit of VaR of no more than $10,000, what are the impacts on your strategy? How is it different
#    from the original strategy without these risk constrains?
#    the drawdown will be smaller, sharpe might be higher
# 5. By the same token, what if you also incorporate a stop-loss limit after |z| >= 4?
#    the drawdown will be smaller, sharpe might be higher

"""
-2
Did not answer question 1 with margin limit with code.
-3
Did not answer question 4 with code.
-2
Did not answer question 5 with code.
"""

import math
import numpy as np
import pandas as pd
from scipy import stats

class Lecture12Homework(QCAlgorithm):

    def Initialize(self):

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
        df1['米+考'] = mu + sigma
        df1['米-考'] = mu - sigma
        
        
        if not self.Portfolio.Invested:        # Enter
            # When W > 米+考, buy Q and sell P
            if df1['W'][-2] > df1['米+考'][-2]:
                self.SetHoldings("GS", -Wp)
                self.SetHoldings("MS", Wq)
            # When W < 米-考, buy P and sell Q
            if df1['W'][-2] < df1['米-考'][-2]:
                self.SetHoldings("GS", Wp)
                self.SetHoldings("MS", -Wq)
        elif abs(df1['W'][-2] - mu) < 0.01:     # Exit When W = 米, Liquidate all the positions
            self.Liquidate("GS")
            self.Liquidate("MS")
            
    def OnData(self, data):
        self.Strategy