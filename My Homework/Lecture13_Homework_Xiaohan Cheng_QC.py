# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 22:06:15 2021

@author: Xiaohan Cheng
"""

# On April 15, 2020, find the option chains for GOOG for all options maturing within 30 days, and +5 and -5 strike prices around ATM options.
# Find all Greeks for these options based on Black-Scholes Formula
# Compute the historical volatility for GOOG with lookback periods = 30, 60 and 90 days. How do they compare to the implied volatilities computed above?
# Please check research.ipynb. Generally, the implied volatility is greater than the historical volatility.


# https://www.quantconnect.com/forum/discussion/3039/value-of-greeks-delta-is-always-0/p1
# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Python/BasicTemplateOptionsHistoryAlgorithm.py

from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Securities.Option import OptionPriceModels
from QuantConnect.Data.UniverseSelection import *
from datetime import timedelta




import pandas as pd
import numpy as np

from QuantConnect.Securities.Option import OptionPriceModels

class Lecture13Homework(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 4, 15)  # Set Start Date
        self.SetEndDate(2020, 4, 15)  #Set End Date
        self.SetCash(1000000)  #Set Strategy Cash
        # The options data is available only in minute resolution, 
        # which means we need to consolidate the data if we wish to work with other resolutions.
        equity = self.AddEquity("GOOG", Resolution.Minute) # Add the underlying stock: Google
        option = self.AddOption("GOOG", Resolution.Minute) # Add the option corresponding to underlying stock
        
        self.symbol = option.Symbol
        # maturing within 30 days, and +5 and -5 strike prices around ATM options
        option.SetFilter(-5, +5, timedelta(0), timedelta(30))
        
        # find more pricing models https://www.quantconnect.com/lean/documentation/topic27704.html
        option.PriceModel = OptionPriceModels.CrankNicolsonFD()
        # set the warm-up period for the pricing model
        self.SetWarmUp(TimeSpan.FromDays(4))
        

    def OnData(self,slice):
        for chain in slice.OptionChains:
            volatility = self.Securities[chain.Key.Underlying].VolatilityModel.Volatility
            for contract in chain.Value:
                self.Log("{0},Bid={1} Ask={2} Last={3} OI={4} sigma={5:.3f} NPV={6:.3f} \
                          delta={7:.3f} gamma={8:.3f} vega={9:.3f} beta={10:.2f} theta={11:.2f} IV={12:.2f}".format(
                contract.Symbol.Value,
                contract.BidPrice,
                contract.AskPrice,
                contract.LastPrice,
                contract.OpenInterest,
                volatility,
                contract.TheoreticalPrice,
                contract.Greeks.Delta,
                contract.Greeks.Gamma,
                contract.Greeks.Vega,
                contract.Greeks.Rho,
                contract.Greeks.Theta, # Theta/365
                contract.ImpliedVolatility))
        '''
        optionchain = chain.Value
        self.Log("underlying price:" + str(optionchain.Underlying.Price))
        
        df = pd.DataFrame([[x.Right,float(x.Strike),x.Expiry,float(x.BidPrice),float(x.AskPrice), x.Greeks.Delta, x.Greeks.Gamma, x.Greeks.Theta, x.Greeks.Vega, x.Greeks.Rho, x.ImpliedVolatility] for x in optionchain],
                    index=[x.Symbol.Value for x in optionchain],
                    columns=['type(call 0, put 1)', 'strike', 'expiry', 'ask price', 'bid price', 'Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'IV'])

        self.Debug(df['Delta'])
        self.Log(str(df))
        '''