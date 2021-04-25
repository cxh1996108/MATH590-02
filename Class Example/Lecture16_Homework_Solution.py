'''
Start with a cash of $1,000,000. Construct a momentum strategy on QC using RSI indicators for WTI Oil Futures.Energies.CrudeOilWTI futures contract with maturity June 2021.
Read the QC documentation first on futures https://www.quantconnect.com/docs/data-library/futures
Use backtesting period 4/2/2020 ¨C 5/1/2020; lookback period for RSI computation is 20 trading days. 
Please identify the optimal entry and exit points that yield the best backtesting result. You have the direction to use daily, or minute resolution as you see fit.

'''
import numpy as np
import pandas as pd

class Rubric_Lecutre16_HW(QCAlgorithm):

    def Initialize(self):
        # backtest 
        
        self.SetStartDate(2020, 4, 2)  
        self.SetEndDate(2020,5,1) 
        self.SetCash(1000000)  # Set Strategy Cash
        
        self.enter = 2 # Set the enter threshold 
        self.exit = 0  # Set the exit threshold 
        self.lookback = 30  # Set the loockback period 90 days
        
        self.future = self.AddFuture(Futures.Energies.CrudeOilWTI, Resolution.Minute)
        self.future.SetFilter(timedelta(0), timedelta(120))
        
        self.lookback = 30 #lookback period for rsi compuration
        self.up=70 #determine the overbough level
        self.dn=30
        
    
    #define our own rsi indicator as it apepars that QC has some problem with futures rsi
    
    def rsi_ind (self, df, lookback):
    
        
        prices = np.array(df["close"])
        delta = prices[1:]-prices[:-1]
        pos = np.sum(delta[delta>0])
        neg = -np.sum(delta[delta<0])
        
        rsi = 100*pos/(pos+neg)
                
        return rsi
        
    def OnData(self, data):

        #Find all the futures contracts added in Initialize() method
        
        self.contract = [contract for chain in data.FutureChains.Values for contract in chain.Contracts.Values if int(contract.Expiry.month) == 6]
        
        self.sym= self.contract[0].Symbol
        
        df = self.History(self.sym, self.lookback)
        
        if (not df.empty):
            
            if (df.count()[0]== self.lookback):
        
                rsi = self.rsi_ind(df, self.lookback)
                
                self.Debug ("Time " + str(self.Time) + " RSI " +str(rsi))
               
                # the following codes are for rsi indicator
                
                if rsi> self.up:
                
                    if self.Portfolio[self.sym].Quantity > 0:
                        self.Liquidate()
                    else:
                        self.SetHoldings(self.sym, -1)
        
                if rsi < self.dn:
        
                    if self.Portfolio[self.sym].Quantity < 0:
                        self.Liquidate()
                    else:
                        self.SetHoldings(self.sym, 1)            
                   
                #output to check on calculations 
                
                #self.Debug ("Time " + str(self.Time) + " Holding " + str(self.Portfolio[self.sym].Quantity) + " " +str(self.sym)+ " rsi " + str(rsi))
                
            self.Debug ("Time is: " + str(self.Time))