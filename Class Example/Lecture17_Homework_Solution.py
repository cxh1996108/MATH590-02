'''
Start with a cash of $1,000,000. Construct a calendar spread strategy on QC for Gold (Futures.Metals.Gold) Futures Contracts, with absolute value of the market values for both long and short positions to be around $500K. 
In this strategy, you always buy the front contract, and sell the third contract. You roll the contract forward 2-days before maturity of the nearer contract. 
Use the backtesting period 4/28/2020 ¨C 6/2/2020; 
Here are the parameters at your discretions:
Stop-loss Threshold ¨C beyond which liquidate your portoflio
Entry point or exit: spread between prices of the first and third contract 
When to long or short which contract. 

'''
import numpy as np
import pandas as pd

class Rubric_Lecutre16_HW(QCAlgorithm):

    def Initialize(self):
        # backtest 
        
        self.SetStartDate(2020, 4, 28)  
        self.SetEndDate(2020,6,2) 
        self.SetCash(1000000)  # Set Strategy Cash
        
        self.future = self.AddFuture(Futures.Metals.Gold, Resolution.Minute)
        self.future.SetFilter(timedelta(0), timedelta(360))
      
        
    def OnData(self, data):

        #Find all the futures contracts added in Initialize() method
        
        self.Debug ("Time " + str (self.Time))
        
        self.contracts = [contract for chain in data.FutureChains.Values for contract in chain.Contracts.Values]
        self.contracts = sorted(self.contracts, key= lambda x : x.Expiry)
        
        if not self.Portfolio.Invested:
            
            #settting up the calendsr spread: long the front and short the back (the third) 
            self.SetHoldings(self.contracts[0].Symbol, 0.5)
            self.SetHoldings(self.contracts[2].Symbol, -0.5)
        
        #roll contracts two days before expiration   
        elif (self.contracts[0].Expiry - self.Time).days <=2:
            
            # rolling of the front contract
            self.SetHoldings(self.contracts[0].Symbol,0)
            self.SetHoldings(self.contracts[1].Symbol,0.5)
            
            #rolling of the back contract if there is a fourth countract in the list.
            
            if len(self.contracts) >=3:
                
                self.SetHoldings(self.contracts[2].Symbol,0)
                self.SetHoldings(self.contracts[3].Symbol,-0.5)
            
                
        self.Debug ("Time " + str(self.Time) + " Holding " + str(self.Portfolio[self.contracts[0].Symbol].Quantity) + " " +str(self.contracts[0].Symbol))