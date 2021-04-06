import numpy as np
import pandas as pd

class UniverseSelection(QCAlgorithm):

    def Initialize(self):
    
        ''' Below are the homework assignments for Lecture 11 on QC
        q1: The top 10 stocks by market capitalization within the industry sector ¡°ConsumerCyclical¡± on 9/9/2019
        q2: The top 10 stocks by dollar trading volume within industry sector ¡°FinancialServices¡± on 9/1/2019
        Top get the answer for Q1, set self.q1 = True; do the same for q2
        '''
 
        self.q1 = False
        self.q2 = True
        
        #define some class variables
        self.mim_px = 10 # minimal price for stock
        
        if self.q1: # to answer question 1
            
            ''' In this case, the selection conditions only touch fine universe, and not coarse universe. 
            As such, youn need to incluse a large coarse universe to avoid imposing any coarse selection restrictions. 
            We set coarse_num = 3000 to indicate we are looking at the top 3000 stock ranked by DollarVolume, essentially 
            a very large universe of stocks.
            '''
            
            self.coarse_num = 3000
            self.fine_num = 10
            self.sector = MorningstarSectorCode.ConsumerCyclical
            
            self.SetStartDate(2019, 9, 9)  # Set Start Date. if it is not a trading day, still yields universe selection, but without data.
            self.SetEndDate(2019, 9, 9)  # Set Start Date 
        
        elif self.q2: #to asnwer question 2
            
            ''' In this situation, the seleciton conditions touch both coarse and fine universes. In coarse universe, we has a list of 
            stocks ranked by DollarVolume, and the in fine universe, we have stocks in financial services. So we need to combine the two universes 
            to find the top financial stocks ranked by DollarVolume. The (ordered, keeping Dollar Volume ranking) intersection
            of these two sests is what we are looking for'''
            
            self.coarse_num = 3000
            self.fine_num = 3000
            self.sector = MorningstarSectorCode.FinancialServices
            
            self.SetStartDate(2019, 9, 1)  # Set Start Date
            self.SetEndDate(2019, 9, 1)  # Set Start Date 
 
        self.AddUniverse(self.CoarseSelectionFilter, self.FineSelectionFunction)
        
        self.UniverseSettings.Resolution = Resolution.Daily

    def CoarseSelectionFilter(self, coarse):
        
        sortedByDollarVolume = sorted(coarse, key=lambda c: c.DollarVolume, reverse=True)
        
        filteredByPrice = [c.Symbol for c in sortedByDollarVolume if c.Price>self.mim_px]
        
        self.filter_coarse = filteredByPrice[:self.coarse_num]
        
        return self.filter_coarse
        
    def FineSelectionFunction(self, fine):
        
         
        # selection based on morningstar sector code, in this example, technology code
        # see document here https://www.quantconnect.com/docs/data-library/fundamentals#Fundamentals-Asset-Classification
    
        fine= [x for x in fine if x.AssetClassification.MorningstarSectorCode == self.sector]
        
        #ranked by the market cap
        
        sortedByMarketCap = sorted(fine, key=lambda c: c.MarketCap, reverse=True)

        filteredFine = [i.Symbol for i in sortedByMarketCap ]
    
        self.filter_fine = filteredFine[:self.fine_num]
        
        return self.filter_fine
        
    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
 
        #create an empty list to store all selected tickers
        self.ticker_list =[]
        
        n= 10
        i =0 
        
        if self.q2:
            
            ''' We find the intersection of self.coarse_filter and self.fine_filter, while keeping the ranking of 
            self.coarse_filter'''
            
            for ticker in self.filter_fine:
                
                if ticker in self.filter_coarse:
    
                    i=i+1
                    self.ticker_list.append(ticker)
                    
                if i>=10:
                    break
                
        elif self.q1:
            
            self.ticker_list =self.filter_fine
            
        stk_list = np.unique(np.array(self.ticker_list))
        
        for ticker in stk_list:
            
            #string = "Time " + str(self.Time)+ " - " + str(ticker)
            
            #string = string + " - Dollar Volume - " + str(self.Securities[ticker].Fundamentals.DollarVolume)
            
            #string = "Time " + str(self.Time) + " Symbol " + str(ticker) + "Invested - " + str(self.Portfolio[ticker].Quantity)
            
            #string = string + " PE Ratio - " + str(self.Securities[ticker].Fundamentals.ValuationRatios.PERatio)
            
            #self.Debug (string) # print to see in the Console
            self.Log(string) # print to a file with full details. Link to the file is at the bottom of Console screen
    
            self.show(ticker)
            
    def show(self, ticker):
        
        self.Debug ("Ticker " + str(ticker))

#==============================================================================================
#==============================================================================================
#==============================================================================================
import math 
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

class Lecture11_HW_Q1Q2(QCAlgorithm):

    def Initialize(self):
        
        '''
        q3: Rank stocks in 1) and 2) by the autocorrelation using daily close data from 1/1/2021 to 3/1/2021
        q4: Rank the stock pairs within 1) and 2) ( that is, pairing two stocks from the same group 1) or 2)) by 
            ADF first then by Bruesch-Paga test using the historical data from 9/1/2020 to 3/1/2021.
            
        if self.q3 ==True, we run q3, else we run q4.
        
        '''
        self.SetStartDate(2021, 3, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
    
        ''' from prior exercies Q1 and Q2, we obtained two stokc lists. self.stocks_cc is the top-10 consumer cyclical stocks 
        ranked by market cao. The second list self.stocks_fs is the top 10 financials with the highest trading volume
        '''
        self.q3 = True
        self.autocorr = False
        
        if self.q3:
            self.len= 39
        else:
            self.len =124
            
        '''These are number of trading days between 1/1/2021, or 9/1/2020 to 3/1/2021. We use pandas.calendar package
        to figure these days, see link https://pandas-market-calendars.readthedocs.io/en/latest/usage.html to install the package
        Also see the example notebook on Duke590 github repo.
        '''
        # These are two stock lists from question1 and question2.
        self.stocks_cc = ["AMZN","BABA", "HD","TOYOY", "MCD","NKE","SBUX","LOW","PCLN","TJX"]
        self.stocks_fs = ["NB", "BRKA","BRKB","TRV","HBC","CMB","MA","PYPL","V","NOB"]
        #create an empty symbols list to store the equity Symbols corresponding to these stock lists.
        
        self.symbols =[]
        
        for ticker in self.stocks_fs:
            
            self.AddEquity(ticker, Resolution.Daily)
            self.symbols.append(self.Symbol(ticker))
        
        # there are 39 trading days between 1/1/2021 - 3/1/2021
        #there are 124 trading days between 9/1/2020 - 3/1/2021
        
        #obtain history of price
        
        self.df = self.History(self.symbols, self.len)
        self.dg = self.df["close"].unstack(level=0)
        
        ''' We first set up empty disctoinary to store autocorrelation and adf. We print the result
        to a log file, which can be retrived at the bottome of Console window'''
        
        if self.autocorr:
            
            acorr ={}
            for ticker in self.stocks_fs:
                
                dh = self.dg[ticker].apply(lambda x: math.log(x)).diff(1)
        
                acorr[ticker] = dh.autocorr(1) #pandas method for calculating autocorrelation
                
            self.Debug(str(acorr))
            
        else:
            
            # Now let us compute the ADF
            
            adf={} #empty dictionary to store adf
            for ticker1 in self.stocks_fs:
                
                for ticker2 in self.stocks_fs:
                    if ticker1 !=ticker2:
                        adf[str(ticker1)+"-"+str(ticker2)] = self.adf(ticker1, ticker2)[1]
                
            self.Debug (str(adf))
        
    def adf(self, ticker1, ticker2):
        
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
        
        return adf
    
    # use statsmodels.stats.diagnostic.het_breuschpagan for Bruesch-Paga test

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''

        # if not self.Portfolio.Invested:
        #    self.SetHoldings("SPY", 1)