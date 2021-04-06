import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import math 
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

'''This is for Lecture 12 Homework. Key requirements are:
1. Start with $200,000 cash  capital. Margin requirement is 50% on both long and short market values.
2. Backtest the Pairs Trading Strategy on QC that you developed in Lecture 10 assignment from 2/1/2020 to 5/1/2020. 
3. For each day of the backtesting period, compute the daily VaR at 95%.
4. If you impose a limit of VaR of no more than $10,000, what are the impacts on your strategy? How is it different from the original strategy without these risk constrains?
5. By the same token, what if you also incorporate a stop-loss limit after |z| >= 4?
'''

class Lecture12_HW_PairsTradingAlgorithm(QCAlgorithm):
    
    def Initialize(self):
       
        self.SetStartDate(2020, 2, 1)
        self.SetEndDate(2020,5,1)
        
        self.SetCash(200000)
        
        self.enter = 1 # Set the enter threshold 
        self.exit = 0  # Set the exit threshold 
        self.lookback = 90  # Set the loockback period 90 days
        self.ci = 0.95 # confidence level for VaR calculation
        self.margin_pct = 0.5
        self.margin_buffer = 0.25
        self.var_limit = 10000
        # lower self.var_limit reduces drawdown and risk, but could also reduce profit as well.
        # The trick is to strike a right balance
        
        self.pairs =['GS','MS']
        self.symbols =[]
        
        for ticker in self.pairs:
            
            self.AddEquity(ticker, Resolution.Daily)
            self.symbols.append(self.Symbol(ticker))
        
    def port_check(self, ticker1, ticker2):
        
        self.df = self.History(self.symbols, self.lookback)
        self.dg = self.df["open"].unstack(level=0)
        
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
        adf = adfuller (res)
        
        return [adf, zscore, slope]
        
    def VarCalc(self, ci, pos1, pos2,beta, dg):
        
        if (pos1 == 0) and (pos2 ==0):
            
            return 0
        else: 
                
            port = dg[self.pairs[0]]*pos1 - dg[self.pairs[1]] *beta*pos2
            
            port_diff = port-port.shift(1)
            
            pnl =pd.DataFrame(data = port_diff).dropna()
    
            pnl['pct_rank'] = pnl.rank(pct=True)
            
            pnl.columns =['daily_pl', 'pct_rank']
            
            pnl = pnl[pnl.pct_rank< 1-ci] # Find the tail distribution
            
            return pnl.daily_pl.max() # the cuto off point is the VaR
        
    def adjusted_wt(self, w1, w2):
        #this function is to show how to calculate the new weight for reducing VaR. It is not being used in the trading.
        #reduce portfolio weight to reduce var usage
        
        pos1 = round(self.equity*w1/self.px1)
        pos2 = round(self.equity*w2/self.px2)
        
        var = self.VarCalc(self.ci, pos1, pos2,self.beta, self.dg )
        adj = min(0, 1-var/self.var_limit)+1
        
        #self.Debug ("Equity is: " + str(self.equity) + " VAR is: " +str(var)+ " wt1 "  + str(w1) +" wt2 "  + str(w2)+ " pos1 "  + str(pos1) +" pos2 "  + str(pos2) )
        
        if var <- self.var_limit:  # adjust the portfolio position size downward
    
            self.Debug (str(var) + " Position Adjusted Down by " + str(adj) )
            
        return [w1*adj, w2*adj]
        
    def OnData(self, data):

        self.IsInvested = (self.Portfolio[self.pairs[0]].Invested) or (self.Portfolio[self.pairs[1]].Invested)
        self.ShortSpread = self.Portfolio[self.pairs[0]].IsShort
        self.LongSpread = self.Portfolio[self.pairs[0]].IsLong
        
        zscore = self.port_check(self.pairs[0], self.pairs[1])[1][-1]
        self.beta = self.port_check(self.pairs[0], self.pairs[1])[2]
        
        self.wt1 = 1/(1+self.beta)
        self.wt2 = self.beta/(1+self.beta)
        
        self.pos1 = self.Portfolio[self.pairs[0]].Quantity
        self.px1 = self.Portfolio[self.pairs[0]].Price
        self.pos2 = self.Portfolio[self.pairs[1]].Quantity
        self.px2 = self.Portfolio[self.pairs[1]].Price
        
        self.equity =self.Portfolio.TotalPortfolioValue
        gross_mkv = abs(self.pos1)*self.px1 + abs(self.pos2)*self.px2
        gross_margin = gross_mkv* self.margin_pct
        
        margin = max(gross_margin, self.Portfolio.TotalMarginUsed)
        
        var = self.VarCalc(self.ci, self.pos1, self.pos2,self.beta, self.dg )
        
        #self.Debug ("VAR Is: " +str(var) + ' Port Margin ' + str(self.Portfolio.TotalMarginUsed) + 'Gross Margin '+ str(gross_margin) )
        
        #self.Debug ("VAR Is: " +str(var) + ' Port_pos1 ' + str(self.pos1) +  ' Port_pos2 ' + str(self.pos2) )
        
        #self.Debug (self.dg.head(1))
        
        entry_condition = (self.equity > margin*(1+self.margin_buffer))
        
        if self.IsInvested:
           
            if self.ShortSpread and zscore <= self.exit or \
                self.LongSpread and zscore >= self.exit:
                self.Liquidate()
                
        elif entry_condition:
           
            #[weight1, weight2] = self.adjusted_wt(weight1, weight2)
            
            if zscore > self.enter:
                
                self.SetHoldings(self.symbols[0], -self.wt1)
                self.SetHoldings(self.symbols[1], self.wt2)   
            
            if zscore < - self.enter:
                
                self.SetHoldings(self.symbols[0], self.wt1)
                self.SetHoldings(self.symbols[1], -self.wt2) 
        else:
            
            pass
        
        #Code below:
        #check if VaR limit is violated, if yes, reduce positions
        #update portfolio positions
    
        self.pos1 = self.Portfolio[self.pairs[0]].Quantity
        self.pos1 = self.Portfolio[self.pairs[0]].Quantity
        
        if self.pos1 !=0 and self.pos2 !=0:
        
            #compute portfolio VaR
            var = self.VarCalc(self.ci, self.pos1, self.pos2,self.beta, self.dg )
            
            # figure out the adujustment factor based on the amount that var is over self.var_limit
            adj= 1/(max(0, -var/self.var_limit-1) +1)
            wt1_adj = self.wt1* (adj-1)
            wt2_adj = self.wt2* (adj-1)
            
            if adj< 1: #if the VaR limit is violated
            
                self.Debug ("Reducing Position to "+  str(adj) + " of target position due to VaR " + str(var) +' > VaR limit of ' +str(self.var_limit))
                
                #incrementally to reduce the position
                
                if self.ShortSpread:
                    self.SetHoldings(self.symbols[0], -wt1_adj)
                    self.SetHoldings(self.symbols[1], wt2_adj)
                else:
                    self.SetHoldings(self.symbols[0], wt1_adj)
                    self.SetHoldings(self.symbols[1], -wt2_adj)
                        
                        
        #print out zscore, positions, to validate the algorithm
        
        string = str(' Time '+ str(self.Time) + ' zscore=' + str(zscore) + " - " + self.pairs[0]) + ' pos=' + str(self.Portfolio[self.pairs[0]].Quantity) + "," + str(self.pairs[1]) + ' pos=' + str(self.Portfolio[self.pairs[1]].Quantity)
        #string = string + " \n VaR is " + str(var*adj) + " vs. a limit of " + str(self.var_limit)
        
        self.Debug("Total Realized PnL: "+ str( self.Portfolio.TotalProfit) + "Total Unrealized: "+ str( self.Portfolio.TotalUnrealizedProfit)+ string)