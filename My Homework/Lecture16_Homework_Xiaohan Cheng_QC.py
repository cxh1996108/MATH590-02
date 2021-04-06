# 1. Start with a cash of $1,000,000. Construct a momentum strategy on QC using RSI indicators for WTI Oil Futures.Energies.CrudeOilWTI futures contract with maturity June 2021.
# 2. Read the QC documentation first on futures https://www.quantconnect.com/docs/data-library/futures
# 3. Use backtesting period 4/2/2020 ¨C 5/1/2020; lookback period for RSI computation is 20 trading days.
# 4. Please identify the optimal entry and exit points that yield the best backtesting result. You have the direction to use daily, or minute resolution as you see fit.

class Lecture16Homework(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 4, 2)  
        self.SetEndDate(2020, 4, 12)
        self.SetCash(1000000)  
        # get the future maturing in June 2020
        self.future = self.AddFuture(Futures.Energies.CrudeOilWTI, Resolution.Minute).SetFilter(timedelta(60), timedelta(90))
        self.lookback = 20
        self.SetWarmUp(20)
    def OnData(self, slice):
        if self.IsWarmingUp:
            return
        contracts = []
        for chain in slice.FutureChains:
            for contract in chain.Value:
                if contract.Expiry.month == 6:
                    contracts.append(contract.Symbol)
        future = contracts[0]
        self.rsi = self.RSI(future, 20,  MovingAverageType.Simple, Resolution.Minute)
        holdings = self.Portfolio[future].Quantity
        '''
        if self.rsi.Current.Value > 70:
            if holdings > 0:
                self.Liquidate()
            else:
                self.SetHoldings(future, -0.5)

        if self.rsi.Current.Value < 30:

            if holdings < 0:
                self.Liquidate()
            else:
                self.SetHoldings(future, 0.5)
        '''
        self.entry = int(self.GetParameter("entry"))
        self.exit = int(self.GetParameter("exit"))
        
        if self.rsi.Current.Value > self.entry:
            if holdings > 0:
                self.Liquidate()
            else:
                self.SetHoldings(future, -0.5)

        if self.rsi.Current.Value < self.exit:

            if holdings < 0:
                self.Liquidate()
            else:
                self.SetHoldings(future, 0.5)