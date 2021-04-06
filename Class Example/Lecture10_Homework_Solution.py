"""
Write a Pairs Trading Strategy that trades on a portfolio of two pairs
of stocks GS vs. MS, and AAPL vs. MSFT, based on the log difference in
prices and the following parameters:

1. Parameters: entry point = 1, exit point = 0. 
Hedge ratio is based on the slope of the linear regression using the rolling 90-day lookback period.

2. Implement the strategy in QuantConnect, and backtest it:
?Backtest your strategy using three 3-month periods: Feb 1 ¨C May 1 in 2018, 2019, and 2020.
?Trading Frequency: Daily
?What can you do on exit or entry point to improve the backtesting pnl performance?
 Articulate the trade-offs between profitability and risk using high or low entry/exit points.
 For example, what are the pros and cons for increasing the entry point from 1 to 2?
?What can you do to decrease the drawdown risk?
"""

import numpy as np
from datetime import timedelta, datetime
import math 
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

# MS vs GS, 
# AAPL vs MSFT is in main2.py
# The strategy is the same, we can distribute half initial cash on each pairs
# cointegration method
class Lecture10_HW_PairsTradingAlgorithm(QCAlgorithm):
    
    
    def Initialize(self):
       
        self.SetStartDate(2018, 2, 1)
        self.SetEndDate(2018,5,1)
        
        self.SetCash(100000)
        
        self.enter = 1 # Set the enter threshold 
        self.exit = 0  # Set the exit threshold 
        self.lookback = 90  # Set the loockback period 90 days
        
        self.pairs =['GS','MS']
        self.symbols =[]
        
        for ticker in self.pairs:
            
            self.AddEquity(ticker, Resolution.Daily)
            self.symbols.append(self.Symbol(ticker))
            
         
    def port_check(self, ticker1, ticker2):
        
        self.df = self.History(self.symbols, self.lookback)
        self.dg = self.df["open"].unstack(level=0) # Pivot a level of the (necessarily hierarchical) index labels.
        
        #self.Debug(self.dg)
        
        Y = self.dg[ticker1].apply(lambda x: math.log(x))
        X = self.dg[ticker2].apply(lambda x: math.log(x))
        
        X = sm.add_constant(X)
        model = sm.OLS(Y,X)
        results = model.fit()
        sigma = math.sqrt(results.mse_resid) # standard deviation of the residual
        slope = results.params[1]
        intercept = results.params[0]
        res = results.resid #regression residual mean of res =0 by definition
        zscore = res/sigma
        adf = adfuller (res) #Augmented Dickey-Fuller unit root test.
        
        return [adf, zscore, slope]
    
    def OnData(self, data):

        self.IsInvested = (self.Portfolio[self.pairs[0]].Invested) or (self.Portfolio[self.pairs[1]].Invested)
        self.ShortSpread = self.Portfolio[self.pairs[0]].IsShort
        self.LongSpread = self.Portfolio[self.pairs[0]].IsLong
        
        zscore = self.port_check(self.pairs[0], self.pairs[1])[1][-1]
        beta = self.port_check(self.pairs[0], self.pairs[1])[2]
        
        if self.IsInvested:
            
            # liquidate all if spread hits exit points
            if self.ShortSpread and zscore <= self.exit or \
                self.LongSpread and zscore >= self.exit:
                self.Liquidate()
        
        else:
            weight1 = 1/(1+beta)
            weight2 = beta / (1+beta)
            
            # spread (z score) larger than upper bound
            if zscore > self.enter:
                # short equity 1, long equity 2.
                self.SetHoldings(self.symbols[0], -weight1)
                self.SetHoldings(self.symbols[1], weight2)   
            
            # spread (z score) smaller than lower bound
            if zscore < - self.enter:
                # long equity 1, short equity 2.
                self.SetHoldings(self.symbols[0], weight1)
                self.SetHoldings(self.symbols[1], -weight2) 
        
 
        #print out zscore, positions, to validate the algorithm
        
        string = str(' Time '+ str(self.Time) + ' zscore=' + str(zscore) + " - " + self.pairs[0]) + ' pos=' + str(self.Portfolio[self.pairs[0]].Quantity) + "," + str(self.pairs[1]) + ' pos=' + str(self.Portfolio[self.pairs[1]].Quantity)
        
        self.Debug("Total Realized PnL: "+ str( self.Portfolio.TotalProfit) + "Total Unrealized: "+ str( self.Portfolio.TotalUnrealizedProfit)+ string)