# Design a strategy that trades every hour, and long 100% in QQQ if 10-day momentum is greater than 50-day momentum
# (moving average), otherwise, hold 100% short position in QQQ. Backtest your result from June 1-July 2021, and use 
# the actual historical data to justify the backtest result.(hint: use self. MOMP())

class Lecture7Homework(QCAlgorithm):

    def Initialize(self):
        
        self.SetStartDate(2020, 6, 1)  
        self.SetEndDate(2020, 7, 1)
        self.SetCash(100000) 
        qqq = self.AddEquity("QQQ", Resolution.Daily)
        
        """
        Wrong algorithm data Resolution -1
        
        qqq = self.AddEquity("QQQ", Resolution.Hour)
        """
        
        qqq.SetDataNormalizationMode(DataNormalizationMode.Raw)
        self.qqqMomentumS = self.MOMP("QQQ", 10, Resolution.Daily)
        self.qqqMomentumL = self.MOMP("QQQ", 50, Resolution.Daily) 
       
        self.SetBenchmark("QQQ")
        
        # trades every hour
        self.Schedule.On(self.DateRules.EveryDay("QQQ"), self.TimeRules.Every(timedelta(minutes = 60)), self.Strategy)
        
        # Warm up algorithm for 10 days to populate the indicators prior to the start date
        self.SetWarmUp(10)
        # Warm up algorithm for 50 days to populate the indicators prior to the start date
        self.SetWarmUp(50) 
        
    def Strategy(self):
        # Design a strategy that trades every hour, and long 100% in QQQ if 10-day momentum is greater than 50-day momentum
        # (moving average), otherwise, hold 100% short position in QQQ.
        
        """
        -1 
        Should be to retrieve data every hour
        self.qqqMomentumS.Current.Value > self.qqqMomentumL.Current.Value
        """
        if self.qqqMomentumS > self.qqqMomentumL:
            # self.Liquidate("QQQ")
            self.SetHoldings("QQQ", 1, True) # True means liquidating other holdings before starting
        # Qtherwise, hold 100% short position in QQQ
        else:
        # self.Liquidate("QQQ")
            self.SetHoldings("QQQ", -1, True)

    def OnData(self, data):
    
        # Don't place trades until our indicators are warmed up:
        if self.IsWarmingUp:
            return
        # You should validate indicators are ready before using them:
        if self.qqqMomentumS is None or self.qqqMomentumL is None or not self.qqqMomentumS.IsReady or not self.qqqMomentumL.IsReady:
            return
        self.Strategy