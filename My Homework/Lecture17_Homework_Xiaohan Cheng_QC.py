# 1. Start with a cash of $1,000,000. Construct a calendar spread strategy on QC for
#    Gold (Futures.Metals.Gold) Futures Contracts, with absolute value of the market values
#    for both long and short positions to be around $500K.
# 2. In this strategy, you always buy the front contract, and sell the third contract. 
#    You roll the contract forward 2-days before maturity of the nearer contract.
# 3. Use the backtesting period 4/28/2020 - 6/2/2020;
# 4. Here are the parameters at your discretions:
#    Stop-loss Threshold - beyond which liquidate your portfolio
#    Entry point or exit: spread between prices of the first and third contract
#    When to long or short which contract.

# https://www.cmegroup.com/trading/metals/precious/gold_contract_specifications.html
# https://www.cmegroup.com/trading/metals/precious/gold_quotes_globex.html

class Lecture17Homework(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 4, 28)  
        self.SetEndDate(2020, 6, 2)
        self.cash = 1000000
        self.SetCash(self.cash) 
        future = self.AddFuture(Futures.Metals.Gold, Resolution.Minute)
        future.SetFilter(timedelta(2), timedelta(180))

    def OnData(self, slice):
        contracts = []
        for chain in slice.FutureChains:
            self.Contracts = [contract for contract in chain.Value]
            sortedContracts = sorted(self.Contracts, key = lambda k : k.Expiry.month, reverse = False)
            for contract in sortedContracts:
                # self.Debug(contract.Expiry)
                contracts.append(contract.Symbol)
        
        front = self.Securities[contracts[0]]
        third = self.Securities[contracts[2]]
        
        # You roll the contract forward 2-days before maturity of the nearer contract.
        if(front.Expiry.day - self.Time.day == timedelta(days = 2)):
            self.Liquidate()
            front = self.Securities[contracts[1]]
            third = self.Securities[contracts[3]]
        
        # Stop-loss Threshold - beyond which liquidate your portfolio
        if self.Portfolio.TotalHoldingsValue < self.cash * 0.8:
            self.Liquidate()
        
        if not self.Portfolio.Invested:
        # Enter
        # In this strategy, you always buy the front contract, and sell the third contract. 
            try:
                if front.AskPrice < third.AskPrice:
                    self.SetHoldings(front.Symbol,  0.3)
                    self.SetHoldings(third.Symbol, -0.3)
            except:
                pass
        # Exit
        elif front.AskPrice > third.AskPrice:
            self.Liquidate()