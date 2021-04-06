import pandas as pd
from QuantConnect.Securities.Option import OptionPriceModels
import math

"""
Implement the following in QC or QB:
- On April 15, 2020, find the option chains for GOOG for all options maturing
  within 30 days, and +5 and -5 strike prices around ATM options.
- Find all Greeks for these options based on Black-Scholes Formula
- Compute the historical volatility for GOOG with lookback periods = 30, 60, and 90 days.
  How do they compare to the implied volatilities computed above ?
"""


class Lecture13HW(QCAlgorithm):

    def Initialize(self):
        
        self.SetStartDate(2019, 4, 15) 
        self.SetEndDate(2019, 4,15)  #Set End Date
        self.SetCash(50000)  #Set Strategy Cash
      
        stock = self.AddEquity("GOOG", Resolution.Minute) # Add the underlying stock: Google
        option = self.AddOption("GOOG", Resolution.Minute) # Add the option corresponding to underlying stock
        
        option.PriceModel = OptionPriceModels.CrankNicolsonFD()
        self.option = option.Symbol
        self.stock = stock.Symbol
        
        self.SetWarmUp(TimeSpan.FromDays(4))
        
        #filter out options only +/- 5 strikes away from ATM, and are within 90 day maturity
        option.SetFilter(-5, +5, timedelta(0), timedelta(90))
        
        #get historical data for historical volatility computation
        df = self.History(self.stock, timedelta(120), Resolution.Daily)
        
        #For the daily return series, that is, using pandas built-in percentage change mathod
        dg = df['close'].pct_change()
        #compute historical vola with 60, 90, 120 days of lookback periods.
        
        for lookback in [60,90,120]:
            
            dh = dg[-1-lookback:-1] # slice out the last lookbak-days of data
            #compute the daily standard deviation and sqaure-root of time rule to compute annualized volatility
            self.hist_vol = dh.std()*math.sqrt(260) 
            self.Debug ("Underlying Stock" + str(self.stock.Value)+ " - " + str(lookback) + " Historical Vol "+ str(self.hist_vol))
        
    
    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        # for each time period, obtain the option chain, and extract greeks and implied vol
        
        for chain in data.OptionChains:
            volatility = self.Securities[chain.Key.Underlying].VolatilityModel.Volatility
            
            if chain.Key != self.option:
                continue
            
            #for each option /contract in option chain, log the greeks and other values.
            for contract in chain.Value:
                
                self.Log("{0},Bid={1} Ask={2} Last={3} OI={4} historical_vol={5:.3f} NPV={6:.3f} \
                          delta={7:.3f} gamma={8:.4f} vega={9:.3f} beta={10:.2f} theta={11:.2f} \
                          IV={12:.2f} stock_px ={13:.2f}".format(
                contract.Symbol.Value,
                contract.BidPrice,
                contract.AskPrice,
                contract.LastPrice,
                contract.OpenInterest,
                self.hist_vol,
                contract.TheoreticalPrice,
                contract.Greeks.Delta,
                contract.Greeks.Gamma,
                contract.Greeks.Vega,
                contract.Greeks.Rho,
                contract.Greeks.Theta, 
                contract.ImpliedVolatility,
                contract.UnderlyingLastPrice))
                
                #self.Debug ("Symbol " + str(contract.Symbol.Value))
                #self.Debug ("Delta " + str(contract.Greeks.Delta))