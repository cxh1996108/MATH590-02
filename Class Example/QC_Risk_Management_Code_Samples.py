'''
The purpose of these code examples is to show how to implement some risk management controls for your algo.
While it is informative to review these codes, it is important to apply them in the context of your own stratrgey.
The point of risk controls is to prevent losses beyond your risk appetities or limits that are set at the beginning. 
In practice, these limits are generally agreed upon between the portfolio manager and investors contractually, and are stricktly observed.

The dilema of risk management is this. On the one hand it does prevent further losses beyond your tolerance. On the other hand,
it also reduces potential upside if market direction reverses. One of the important decision is to decide when you should get back in when 
a risk limit is triggered that causes liquidation of your positions. At least, when risk limits are triggered, you should take a break to reassess 
the situation before continue on.


'''

import numpy as np
import pandas as pd
class ExamplesonRiskControls(QCAlgorithm):

    def Initialize(self):
        
        self.SetStartDate(2020, 5, 1)  # Set Start Date
        self.SetEndDate(2020, 7, 1)  # Set Start Date
        
        self.init_equity = 100000
        self.SetCash(self.init_equity)  # Set Strategy Cash
        
        self.vt = []
        self.symbols =[]
        self.wt_vt = {}
        self.exit_test = False
        
        self.var_limit = 0.1
        self.sigma_limit = 0.05
        self.stop_loss_limit = 0.15
        self.ci = 0.95
        self.lookback = 90
        self.max_drawdown_limit = 0.2
        
        self.drawdown_test = False
        self.cumpl_test = False
        self.sigma_test = False
        self.var_test =False
        
        self.exit_test = False
        
        self.stocks =['SPY','QQQ', 'GOOG', 'XOM']
        
        for ticker in self.stocks:
            
            sym = self.AddEquity(ticker, Resolution.Daily)
            self.symbols.append(self.Symbol(ticker))
            
    def VarCalc(self, pos, wt, lookback, ci = 0.99):
        #Calculate VaR and Sigma based on historical data with lookback period =lookback and confidence interval ci
        
        #get historical data for an array of symbols pos
        self.df = self.History(pos, lookback)
        
        #flatten out the dataset with each column representing a particular stock
        self.dg = self.df["close"].unstack(level=0)
        
        #create a column for the historical portfolio values
        self.dg['port'] = 0 
        
        for ticker in pos:
            
            self.dg['port'] = self.dg['port'] + self.dg[ticker]*self.wt_vt[ticker]*self.Portfolio[ticker].Quantity
        
        
        #if there is no position, we set both to zero
        if not self.Portfolio.Invested:
            
            return [0,0]
        else: 
                
            port = self.dg['port']
            
            port_diff = port-port.shift(1)
            
            pnl =pd.DataFrame(data = port_diff).dropna()
            
            sigma = pnl.std()
    
            pnl['pct_rank'] = pnl.rank(pct=True)
            
            pnl.columns =['daily_pl', 'pct_rank']
            
            pnl = pnl[pnl.pct_rank< 1-ci] # Find the tail distribution
            
            var = pnl.daily_pl.max() #Value-at-Risk within the confidendence interval ci
            
            return [sigma,var]

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        #Check of you should open positions
        
        if (not self.Portfolio.Invested) and not self.exit_test:
            
            n = len(self.stocks)
            wt = 1/n
            
            for ticker in self.symbols:
                self.wt_vt[ticker] = wt
                self.SetHoldings(ticker, wt)
            
        #self.Debug ("Unrealized " +str(self.Portfolio.TotalUnrealizedProfit ) +" Realized " + str(self.Portfolio.TotalProfit) + " Equity "+ str(self.Portfolio.TotalPortfolioValue)
        
        [sigma, var] = self.VarCalc(self.symbols, self.wt_vt, self.lookback,self.ci)
        
        self.Debug (" Var " +str (var) + " Sigma " +str(sigma))
        
        self.cum_pl = self.Portfolio.TotalUnrealizedProfit +self.Portfolio.TotalProfit
        self.vt.append(self.cum_pl)
       
        self.pl = np.array(self.vt)
        
        maxx = self.pl.max()
        minn = self.pl.min()
        self.maxdrawdown = maxx - minn
        
        current_equity = self.Portfolio.TotalPortfolioValue
        
        try:
            self.drawdown_test = self.maxdrawdown> self.init_equity*self.max_drawdown_limit
            self.cumpl_test= self.cum_pl<- self.init_equity*self.stop_loss_limit
            self.sigma_test = sigma > current_equity*self.sigma_limit
            self.var_test = var < -current_equity*self.var_limit
            
            #exit trading by liquidating portfolio if one of these tests is true
            
            self.exit_test = self.drawdown_test or self.cumpl_test or self.sigma_test or self.var_test
        
        except:
            
            self.Debug ("Time " +str(self.Time) + "Error ")
        
        #printout the message to see which test failes exactaly that caused the trading exit.
        
        if self.exit_test:
            
            self.Debug ("Liquidation due to Exit Test on " +str(self.Time))
            
            self.Debug("dradown_test " + str(self.drawndown_test))
            self.Debug("cumpl_test " + str(self.cumpl_test))
            self.Debug("sigma_test " + str(self.sigma_test))
            self.Debug("var_test " + str(self.var_test))
        
            self.Liquidate()