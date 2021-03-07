# -*- coding: utf-8 -*-

# Develop a momentum Strategy base on a moment strategy on two of your favorite stocks. 
# Suggest one for high grow tech stocks like ROKU, TDOC, or CRWD and one for a market index like SPY, QQQ or DIA.

# You can choose either RSI or BollingerBands(BB) as your indicators. If your group number is odd, you should use RSI, otherwise use BB.
# However, you are also encouraged to try both.

# You have a choice of parameters of rolling window, and RSI entry and exit thresholds if RSI is chosen 
# or the width of the BB band(2 sigma or something different) if using BB.
# Find the optimal ones and justify your answer based on backtesting.

# On QuantConnect, use the past 3 years of daily data to back test your strategy by separating data in to in and out sample sets.


# Algorithm Reference Indicators https://www.quantconnect.com/docs/algorithm-reference/indicators

class Lecture9Homework(QCAlgorithm):

    def Initialize(self):
        '''
        # In-sample data set
        self.SetStartDate(2018, 2, 1)
        self.SetEndDate(2020, 2, 1)
        '''
        
        # Out of sample data
        self.SetStartDate(2020, 2, 1)  
        self.SetEndDate(2021, 2, 1)
        
        
        self.SetCash(100000) 
        
        
        self.bili = self.AddEquity("BILI", Resolution.Daily)
        self.qqq = self.AddEquity("QQQ", Resolution.Daily)
        self.qqq.SetDataNormalizationMode(DataNormalizationMode.Raw)
        self.bili.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
        '''
        # BandWidth is k sigma
        # Rolling Window is w days
        # https://www.quantconnect.com/blog/cloud-optimization-now-available-on-quantconnect/
        self.bandwidth = int(self.GetParameter("k"))
        self.window = int(self.GetParameter("w"))
        self.bb = self.BB(self.bili.Symbol, self.window, self.bandwidth, MovingAverageType.Simple, Resolution.Daily)
        '''
        # The optimized BandWidth is 3 sigma
        # The optimized Rolling Window is 16 (or 17, but I will choose 16)
        self.bandwidth = int(self.GetParameter("k"))
        self.window = int(self.GetParameter("w"))
        self.bb = self.BB(self.bili.Symbol, self.window, self.bandwidth, MovingAverageType.Simple, Resolution.Daily)
        
        
        
        
        self.SetBenchmark("QQQ")
        
        
        # trades every day
        self.Schedule.On(self.DateRules.EveryDay("BILI"), self.TimeRules.AfterMarketOpen("BILI"), self.Strategy)
        # self.Schedule.On(self.DateRules.EveryDay("QQQ"), self.TimeRules.Every(timedelta(minutes = 60)), self.Strategy)
        # Warm up algorithm for 10 days to populate the indicators prior to the start date
        self.SetWarmUp(20)
 
        
        """
        # RSI Indicators
        # define a 10-period daily RSI indicator with shortcut helper method
        self.rsi = self.RSI("BILI", 10,  MovingAverageType.Simple, Resolution.Daily)
        # set a warm-up period to initialize the indicator
        self.SetWarmUp(10, Resolution.Daily)
        """
        
    def Strategy(self):
        
        '''
        # Buy if current stock price is lower than lower band
        # Remember to use Current.Value. It is wrong if you don't use it.
        if self.bb.LowerBand.Current.Value > self.bili.Price:
            # self.Liquidate("QQQ")
            self.SetHoldings("BILI", 1, True) # True means liquidating other holdings before starting
        # Sell if current stock price is higher than upper band
        if self.bb.UpperBand.Current.Value < self.bili.Price:
            self.SetHoldings("BILI", -1, True)
        '''
    
        # Buy if current stock price is higher than upper band
        if self.bb.UpperBand.Current.Value < self.bili.Price:
            self.SetHoldings("BILI", 1, True)
        # Sell if current stock price is lower than lower band
        if self.bb.LowerBand.Current.Value > self.bili.Price:
            # self.Liquidate("QQQ")
            self.SetHoldings("BILI", -1, True) # True means liquidating other holdings before starting
        
        """
        -0
        It is better if we use the self.Price field of BB indicator to get the Price level (IndicatorBase)
        e.g. self.spyBB.LowerBand.Current.Value > self.spyBB.Price.Current.Value
        """
        
    def OnData(self, data):
    
        # Don't place trades until our indicators are warmed up:
        if self.IsWarmingUp:
            return
        # You should validate indicators are ready before using them:
        if not self.bb.IsReady:
            return
        self.Strategy
        