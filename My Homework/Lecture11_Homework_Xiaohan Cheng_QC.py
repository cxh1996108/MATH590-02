# -*- coding: utf-8 -*-
"""

@author: Xiaohan Cheng
"""

# Use university selection to find:
# 1) The top 10 stocks by market capitalization within the industry sector "ConsumerCyclical" on 9/9/2019
# ["AMZN", "BABA", "HD", "TOYOY", "MCD", "NKE", "SBUX", "LOW", "PCLN", "TJX"]

# 2) The top 10 stocks by dollar trading volume within the industry sector "FinancialServices" on 9/1/2019
# This is wrong ["NB", "CMB", "NOB", "V", "TRV", "BRKB", "MA", "PYPL", "MHP", "ACL"]
# ["NB", "CMB", "TRV", "NOB", "V", "BRKB", "MA", "PYPL", "MHP", "ACL"]

# 3) Rank stocks in 1) and 2) by the autocorrelation using daily close data from 1/1/2021 to 3/1/2021
# 4) Rank the stock pairs within 1) and 2) (that is, pairing two stocks from the same group 1) or2)) by ADF first 
#    then by Bruesch-Pagan test using the historical data from 9/1/2020 to 3/1/2021

# https://www.quantconnect.com/docs/algorithm-framework/universe-selection#Universe-Selection-Fundamental-Universe-Selection
# https://www.quantconnect.com/docs/algorithm-reference/universes

class Lecture11(QCAlgorithm):

    
    filteredByPrice = None
    
    def Initialize(self):
        self.SetStartDate(2019, 8, 27)  
        self.SetEndDate(2019, 9, 5) 
        self.SetCash(100000)  
        self.AddUniverse(self.CoarseSelectionFilter, self.FineSelectionFunction)
        self.UniverseSettings.Resolution = Resolution.Daily
        '''
        universe = ["AMZN", "BABA", "HD", "TOYOY", "MCD", "NKE", "SBUX", "LOW", "PCLN", "TJX"]
        for symbol in universe:
            self.symbol = self.AddEquity(symbol, Resolution.Daily)
            history = self.History(self.symbol, 38, Resolution.Daily)
            # Can also write like this: apply(lambda x: math.log(x))
            self.log[symbol] = np.log(history.loc[symbol].close)
            self.log_diff[symbol] = np.diff(self.log[symbol])
        '''
        # For simple requests, you can use the functional implementation of the security initializer
        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))
    '''
    def CustomSecurityInitializer(self, security):
    # Initialize the security with raw prices
        security.SetDataNormalizationMode(DataNormalizationMode.Raw)
    '''
    
    '''
    # 1) The top 10 stocks by market capitalization within the industry sector "ConsumerCyclical" on 9/9/2019
    def CoarseSelectionFilter(self, coarse):
        filtered = [c.Symbol for c in coarse if c.HasFundamentalData]
        self.filter_coarse = filtered
        return filtered
    def FineSelectionFunction(self, fine):
        # Selection based on morningstar sector code "ConsumerCyclical"
        # https://www.quantconnect.com/docs/data-library/fundamentals#Fundamentals-Asset-Classification
        fine = [x for x in fine if x.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.ConsumerCyclical]
       
        # Selection based on market capitalization
        sortedByMarketCap = sorted(fine, key=lambda c: c.MarketCap, reverse=True) 
        # The top 10 stocks by market capitalization
        filteredFine = [i.Symbol for i in sortedByMarketCap][:10]
        self.filter_fine = filteredFine
        return filteredFine
    '''
    
    # 2) The top 10 stocks by dollar trading volume within the industry sector "FinancialServices" on 9/1/2019
    
    def CoarseSelectionFilter(self, coarse):
        filtered = [c for c in coarse if c.HasFundamentalData and c.DollarVolume > 0]
        sortedByDollarVolume = sorted(filtered, key=lambda c: c.DollarVolume, reverse=True)
        self.filter_coarse = [i.Symbol for i in sortedByDollarVolume]
        return [i.Symbol for i in sortedByDollarVolume]
    def FineSelectionFunction(self, fine):
        # Selection based on morningstar sector code "FinancialServices"
        # https://www.quantconnect.com/docs/data-library/fundamentals#Fundamentals-Asset-Classification
        fine = [x for x in fine if x.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.FinancialServices]
        filteredFine = [i.Symbol for i in fine][:10]
        self.filter_fine = filteredFine
        return filteredFine
    
    
    # This allows your algorithm to know the changes in the universe state.
    def OnSecuritiesChanged(self, changes):
        self._changes = changes
        self.Log(f"OnSecuritiesChanged({self.UtcTime}):: {changes}")
        
    def OnData(self, data):

        self.Debug(" Length of "+ str(len(self.filter_fine)))
        
        for ticker in self.filter_fine:
            self.Debug ("Time " + str(self.Time) + " Symbol " + str(ticker) + "Invested - "+ str(self.Portfolio[ticker].Quantity))
        pass