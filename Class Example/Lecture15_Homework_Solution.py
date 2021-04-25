"""
Start with a cash of $1,000,000. Construct a pairs trading strategy using the pair of futures contracts: emini S&P and emini NASDAQ futures contracts.
The contract codes for these two contracts on QC are: Futures.Indices.SP500EMini and Futures.Indices.NASDAQ100EMini.
Note: the contract multipliers are 50 and 20, respectively for these two contracts.
These are 10 times of the Micro Emini Contracts mentioned above
Read the QC documentation first on futures https://www.quantconnect.com/docs/data-library/futures
Use the contract maturity for both futures for March 2021 maturity. 
Assume hedge ratio = 1, and market value of each side is $500,000.
Assume entry zscore = 2, exit zscore = 0.
Use backtesting period 1/2/2021 ¨C 3/1/2021; 
All other parameters are discretionary such as necessary risk management controls to void large drawdown risks. 

"""

import numpy as np
from datetime import timedelta, datetime
import math 
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

# ES vs NQ Emini Futures, 
# cointegration method
# forced hedge ratio =1

class Lecture15_HW_PairsTradingAlgorithm(QCAlgorithm):
    
    
    def Initialize(self):
       
        self.SetStartDate(2021, 1,2)
        self.SetEndDate(2021,3,1)
        
        self.capital = 1000000
        
        self.SetCash(self.capital)
        
        self.enter = 4
        '''
        Because futures resolution is 1 minute, we need to set higher entry point to be profotable
        The sigma is around 1-2 basis point, and as such, we have to set exit at least 4 to make sense accounting for 
        transaction costs.
        '''
        self.exit = 0  # Set the exit threshold 
        self.lookback = 30  # Set the loockback period 30 days
        self.max_loss = 0.2 # the largest drawdown before we liquidate positions
        
        #add two futures contracts for S&P and Nasdaq emini contracts
        self.future1 = self.AddFuture(Futures.Indices.SP500EMini, Resolution.Minute)
        self.future2 = self.AddFuture(Futures.Indices.NASDAQ100EMini, Resolution.Minute)
        #filter out contracts beyond 120 days
        self.future1.SetFilter(timedelta(0), timedelta(120))
        self.future2.SetFilter(timedelta(0), timedelta(120))
        
    def port_check(self, df):
        
        self.df = df
        self.dg = self.df["open"].unstack(level=1) # Pivot a level of the (necessarily hierarchical) index labels.
    
        
        Y = self.dg.iloc[:,0].apply(lambda x: math.log(x))
        X = self.dg.iloc[:,1].apply(lambda x: math.log(x))
        
        '''
        Z = sm.add_constant(X)
        model = sm.OLS(Y,Z)
        results = model.fit()
        sigma = math.sqrt(results.mse_resid) # standard deviation of the residual
        slope = results.params[1]
        intercept = results.params[0]
        res = results.resid #regression residual mean of res =0 by definition
        adf = adfuller (res) #Augmented Dickey-Fuller unit root test.
        zscore = res/sigma
        '''
        #self.Debug ("Length " + str(self.dg.count()[0]))
        
        #force the slope =1
        res = Y-X
        avg = res.mean()
        sigma = res.std()
        slope =1
        zscore =  (res-avg)/sigma
        adf = adfuller (res)
        
        return [adf, zscore, slope, sigma]
    
    def OnData(self, data):

        #Find all contracts that meet certain conditions
        self.symbols = [contract.Symbol for chain in data.FutureChains.Values for contract in chain.Contracts.Values if int(contract.Expiry.month) == 3]
        #check to see if we hold these futures positions
        self.IsInvested = (self.Portfolio[self.symbols[0]].Invested) or (self.Portfolio[self.symbols[1]].Invested)
        self.ShortSpread = self.Portfolio[self.symbols[0]].IsShort
        self.LongSpread = self.Portfolio[self.symbols[0]].IsLong
        
        #get historical data
        df = self.History([self.symbols[0], self.symbols[1]], self.lookback)
        #check if they are empty or missing data
        if (not df.empty):
            if (df.count()[0]== 2*self.lookback):
            
                [adf, zscore, slope, sigma] = self.port_check(df)
                
                zscore = zscore[-1]
                #fore slope =1
                beta= 1
                #beta = self.port_check(self.symbols[0], self.symbols[1])[2]
            
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
                        # short equit 1, long equit 2.
                        self.SetHoldings(self.symbols[0], -weight1)
                        self.SetHoldings(self.symbols[1], weight2)   
                    
                    # spread (z score) smaller than lower bound
                    if zscore < - self.enter:
                        # long equit 1, short equit 2.
                        self.SetHoldings(self.symbols[0], weight1)
                        self.SetHoldings(self.symbols[1], -weight2) 
                        
                        
                unrealized = self.Portfolio.TotalUnrealizedProfit
                realized = self.Portfolio.TotalProfit
                
                #stop-loss: if the loss is more than the max_loss threshold, liquidate all positions
                
                
                if unrealized + realized <-self.max_loss*self.capital:
                    
                    self.Liquidate()

     
                #print out zscore, positions, to validate the algorithm
            
                #string = ' Time '+ str(self.Time) + ' zscore=' + str(zscore) + " - " + str(self.symbols[0]) + ' pos=' + str(self.Portfolio[self.symbols[0]].Quantity) + "," + str(self.symbols[1]) + ' pos=' + str(self.Portfolio[self.symbols[1]].Quantity)
            
                self.Debug ("Time " + str(self.Time) +' zscore=' + str(zscore)  +' sigma=' + str(sigma*10000) +" Total Realized PnL: "+ str(unrealized+realized) + ' threshold ' + str(-self.max_loss*self.capital))
            
        #self.Debug ("Time is: " + str(self.Time) + " Length " + str(df.count()[0]))