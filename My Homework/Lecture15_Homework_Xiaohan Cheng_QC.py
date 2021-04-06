# 1. Start with a cash of $1,000,000. Construct a pairs trading strategy using the pair of futures contracts: emini S&P and emini NASDAQ futures contracts.
# 2. The contract codes for these two contracts on QC are: Futures.Indices.SP500EMini and Futures.Indices.NASDAQ100EMini. 
#    Note: the contract multipliers are 50 and 20, respectively for these two contracts. These are 10 times of the Micro Emini Contracts mentioned above
# 3. Read the QC documentation first on futures https://www.quantconnect.com/docs/data-library/futures
# 4. Use the contract maturity for both futures for March 2021 maturity.

# 5. Assume hedge ratio = 1, and market value of each side is $500,000.
# 6. Assume entry zscore = 2, exit zscore = 0.
# 7. Use backtesting period 1/2/2021 ¨C 3/1/2021;
# 8. All other parameters are discretionary such as necessary risk management controls to void large drawdown risks.


import math
import numpy as np
import pandas as pd
from scipy import stats
        
class Lecture15Homework(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2021, 2, 1)  
        self.SetEndDate(2021, 2, 10)
        self.SetCash(1000000)  
        self.lookback = 30
        future1 = self.AddFuture(Futures.Indices.SP500EMini)
        future2 = self.AddFuture(Futures.Indices.NASDAQ100EMini)
        future1.SetFilter(timedelta(0), timedelta(60))
        future2.SetFilter(timedelta(0), timedelta(60))
        
        
        
        
        self.ci = 0.95 # confidence level for VaR calculation
        self.beta = 1 # Assume hedge ratio = 1
        self.var_limit = 100000 # lower self.var_limit reduces drawdown and risk, but could also reduce profit as well.
        
        self.wt1 = 0.5
        self.wt2 = 0.5
        
    def port_check(self, contract1, contract2): 
        self.hist1 = self.History(contract1, self.lookback)
        self.hist2 = self.History(contract2, self.lookback)
        # self.Debug(self.hist2)

        # in case that sometimes the hist doesn't contain 'close' or miss data
        try:
            y = np.array(np.log(self.hist1["close"]))
            x = np.array(np.log(self.hist2["close"]))
            #Assume hedge ratio = 1
            e = y - x
            mu = e.mean()
            sigma = np.std(e)
            self.dg = pd.DataFrame()
            self.dg[self.pairs[0]] = y
            self.dg[self.pairs[1]] = x
        except:
            zscore = None
        else:
            zscore = (e[-1]-mu)/sigma
        
        # self.Debug(self.dg)

        return zscore
    
    def VarCalc(self, ci, pos1, pos2, beta, dg):
        
        if (pos1 == 0) and (pos2 == 0):
            return 0
        else: 
            self.Debug("Hello")
            port = dg[self.pairs[0]] * pos1 - dg[self.pairs[1]] * beta * pos2
            port_diff = port-port.shift(1)
            pnl =pd.DataFrame(data = port_diff).dropna()
            pnl['pct_rank'] = pnl.rank(pct=True)
            pnl.columns =['daily_pl', 'pct_rank']
            pnl = pnl[pnl.pct_rank< 1-ci] # Find the tail distribution
            return pnl.daily_pl.max() # the cut off point is the VaR
    
    
    def OnData(self, slice):
        contract_pair = []
        for chain in slice.FutureChains:
            for contract in chain.Value:
                if contract.Expiry.month == 3:
                    contract_pair.append(contract.Symbol)
        # self.Debug(contract_pair)
        self.pairs = contract_pair
        
        # Flag
        self.ShortSpread = self.Portfolio[self.pairs[0]].IsShort
        
        zscore = self.port_check(contract_pair[0], contract_pair[1])
        
        self.pos1 = self.Portfolio[self.pairs[0]].Quantity
        self.px1 = self.Portfolio[self.pairs[0]].Price
        self.pos2 = self.Portfolio[self.pairs[1]].Quantity
        self.px2 = self.Portfolio[self.pairs[1]].Price
        
        # self.equity =self.Portfolio.TotalPortfolioValue
        # gross_mkv = abs(self.pos1) * self.px1 + abs(self.pos2) * self.px2
        # var = self.VarCalc(self.ci, self.pos1, self.pos2, self.beta, self.dg )
        
        if zscore == None: 
            return
        # Enter
        if not self.Portfolio.Invested:   
            #Assume entry zscore = 2
            if zscore > 2:
                self.SetHoldings(contract_pair[0], -self.wt1)
                self.SetHoldings(contract_pair[1],  self.wt2)
            elif zscore < -2:
                self.SetHoldings(contract_pair[0],  self.wt1)
                self.SetHoldings(contract_pair[1], -self.wt2)
        
        # Exit 
        # Assume exit zscore = 0
        elif abs(zscore) < 0.01:  
            self.Liquidate(contract_pair[0])
            self.Liquidate(contract_pair[1])
        var = self.VarCalc(self.ci, self.pos1, self.pos2, self.beta, self.dg)
        # self.Debug(var)
    
    
        # Adjustment based on VaR
        if self.pos1 !=0 and self.pos2 !=0:
            # compute portfolio VaR
            var = self.VarCalc(self.ci, self.pos1, self.pos2, self.beta, self.dg )
            
            # figure out the adujustment factor based on the amount that var is over self.var_limit
            adj= 1/(max(0, -var/self.var_limit-1) +1)
            wt1_adj = self.wt1 * (adj-1)
            wt2_adj = self.wt2 * (adj-1)
            
             # If the VaR limit is violated
            if adj< 1:
                self.Debug ("Reducing Position to "+  str(adj) + " of target position due to VaR " + str(var) +' > VaR limit of ' +str(self.var_limit))
                
                # incrementally to reduce the position
                if self.ShortSpread:
                    self.SetHoldings(contract_pair[0], -wt1_adj)
                    self.SetHoldings(contract_pair[1],  wt2_adj)
                else:
                    self.SetHoldings(contract_pair[0],  wt1_adj)
                    self.SetHoldings(contract_pair[1], -wt2_adj)