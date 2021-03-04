class LiquidUniverseSelection(QCAlgorithm):
    
    filteredByPrice = None
    
    def Initialize(self):
        self.SetStartDate(2020, 1, 11)  
        self.SetEndDate(2020, 3, 1) 
        self.SetCash(100000)
        # Addiing a universe based on two joint selections: self.CoarseSelectionFilter and self.FineSelectionFunction
        
        self.AddUniverse(self.CoarseSelectionFilter, self.FineSelectionFunction)
        self.UniverseSettings.Resolution = Resolution.Daily
      
        self.SetSecurityInitializer(lambda x: x.SetDataNormalizationMode(DataNormalizationMode.Raw))

        #1. Set the leverage to 2
        
        self.UniverseSettings.Leverage = 2
        
        self.Liquidate()
                
       
    def CoarseSelectionFilter(self, coarse):
        
        # selection based on highest trading volume with price >$10
        
        sortedByDollarVolume = sorted(coarse, key=lambda c: c.DollarVolume, reverse=True)
        filteredByPrice = [c.Symbol for c in sortedByDollarVolume if c.Price > 10]
        
        self.filter_coarse = filteredByPrice
        
        return filteredByPrice[:500] 
        
    def FineSelectionFunction(self, fine):
        
        # selection based on morningstar sector code, in this example, technology code
        # see document here https://www.quantconnect.com/docs/data-library/fundamentals#Fundamentals-Asset-Classification
        
        fine = [x for x in fine if x.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.Technology]
        #fine = [x for x in fine if x.AssetClassification.MorningstarIndustryCode == MorningstarIndustryCode.Semiconductors]
        
        filteredFine = [i.Symbol for i in fine ]
        
        self.filter_fine = filteredFine
        
        return filteredFine
        
    def OnSecuritiesChanged(self, changes):
        self.changes = changes
        
        for security in self.changes.RemovedSecurities:
            
            if security.Invested:
                self.Liquidate(security.Symbol)
                #self.Debug(str(security.Symbol) + " is removed")
        
        for security in self.changes.AddedSecurities:
            #2. Leave a cash buffer by setting the allocation to 0.18 instead of 0.2 
            # self.SetHoldings(security.Symbol, ...)
            
            #self.Debug ()
            
            if not self.Portfolio[security.Symbol].Invested:
                
                self.SetHoldings(security.Symbol, 0.05)
            
                if self.Portfolio[security.Symbol].Quantity != 0:
                    self.Debug(str(security.Symbol) + " is added with positions " + str(self.Portfolio[security.Symbol].Quantity))
            
    def OnData(self, data):

        #self.Log(f"OnData({self.UtcTime}): Keys: {', '.join([key.Value for key in data.Keys])}")

        # if we have no changes, do nothing
        #if self._changes is None: return"Invested - "+ str(self.Portfolio[security.Symbol].Invested)

        # liquidate removed securities
        #for security in self._changes.RemovedSecurities:
            #if security.Invested:
                #self.Liquidate(security.Symbol)
                
        self.Debug(" Length of "+ str(len(self.filter_fine)))
        
        for ticker in self.filter_fine:
            
            self.Debug ("Time " + str(self.Time) + " Symbol " + str(ticker) + "Invested - "+ str(self.Portfolio[ticker].Quantity))