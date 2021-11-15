import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import math 
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
import selected_pairs
import ta
import matplotlib.pyplot as plt
from pykalman import KalmanFilter

class PairsTradingAlgorithm(QCAlgorithm):
    
    def Initialize(self):
       
        self.SetStartDate(2018, 1, 2)
        self.SetEndDate(2021, 4, 15)
        
        self.cash = 1000000
        self.SetCash(self.cash)
        
        
        self.enter = float(self.GetParameter("enter"))
        self.exit = float(self.GetParameter("exit"))
        
        
        
        # self.enter = enter # Set the enter threshold 
        # self.exit = exit # Set the exit threshold 
        
        self.stop_loss = 4
        self.lookback = 30  # Set the loockback period 90 days
        self.ci = 0.95 # confidence level for VaR calculation
        self.margin_pct = 0.5
        self.margin_buffer = 0.25
        self.var_limit = 30000
        self.max_loss = 0.15
        # lower self.var_limit reduces drawdown and risk, but could also reduce profit as well.
        # The trick is to strike a right balance
       
        self.selected = selected_pairs.selected_test4
        
        self.num = len(self.selected) # number of pairs
        self.cash_per_pair = self.cash/self.num
        
        
        self.symbols =[]
        keys = []
        for pair in self.selected:
            for ticker in pair:
                self.AddEquity(ticker, Resolution.Daily)
                self.symbols.append(self.Symbol(ticker))

            keys.append(pair[0] + ', ' + pair[1]) # keys of the PnL DataFrame
        values = [pd.DataFrame(columns = ['pos1', 'pos2', 'px1', 'px2','PnL'])] * self.num # values of the PnL DataFrame
        self.pair_pnl = dict(zip(keys, values)) # Initialize the PnL DataFrame for a certain pair
        #self.Debug(self.pair_pnl)
    
        # Gold Trading Strategy #####################
        self.gold_symbols = []
        self.gold_pair = ['SPY', 'SGOL']
        for ticker in self.gold_pair:
            self.AddEquity(ticker, Resolution.Daily)
            self.gold_symbols.append(self.Symbol(ticker))
        self.window = 5
        #############################################    
    
    def slope_kalman(self, pairs):
        
        prices = (self.History(pairs, self.lookback))["open"].unstack(level=0)
        self.dg = prices
        delta = 1e-5 # 控制过渡协方差矩阵的噪音
        trans_cov = delta / (1 - delta) * np.eye(2) # 过渡协方差矩阵
        # 创建观测矩阵：一个一维矩阵存储TFT的值
        obs_mat = np.vstack(
            [prices[pairs[1]], np.ones(prices[pairs[1]].shape)]
        ).T[:, np.newaxis]
        # 创建卡尔曼滤波器实例

        kf = KalmanFilter(
            n_dim_obs=1, 
            n_dim_state=2,#状态，这里是2，我们要求的是线性回归的斜率和截距
            initial_state_mean=np.zeros(2),#斜率和截距的状态均值初始化为0
            initial_state_covariance=np.ones((2, 2)),
            transition_matrices=np.eye(2),
            observation_matrices=obs_mat,#观测矩阵
            observation_covariance=1.0,
            transition_covariance=trans_cov
            )
        # 调用过滤器。计算截距和斜率的状态。
        state_means, state_covs = kf.filter(prices[pairs[0]].values)
        slope = state_means[:, 0][-1]
        intercept = state_means[:, 1]
        df_spread = prices[pairs[0]] - prices[pairs[1]] * slope - intercept # df_spread is a series, we need the last one.
        spread = df_spread[-1]
        mu = (prices[pairs[0]] - prices[pairs[1]] * slope - intercept).mean()
        sigma = (prices[pairs[0]] - prices[pairs[1]] * slope - intercept).std()
        df_zscore = (df_spread - mu)/sigma
        zscore = (spread - mu)/sigma
        return [zscore, slope]
        
    
    def port_check(self, ticker1, ticker2):
        
        pairs = [ticker1, ticker2]
        self.df = self.History(pairs, self.lookback)
        self.dg = self.df["open"].unstack(level=0)
        
        #self.Debug(self.dg)
        
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
        return [adf, zscore, slope]
    
    def VarCalc(self, pairs, ci, pos1, pos2, dg):
        if (pos1 == 0) and (pos2 == 0):
            return [0, 0]
        else: 
            port = dg[pairs[0]] * pos1 + dg[pairs[1]] * pos2
            port_diff = port - port.shift(1)
            pnl =pd.DataFrame(data = port_diff).dropna()
            pnl['pct_rank'] = pnl.rank(pct=True)
            pnl.columns =['daily_pl', 'pct_rank']
            daily_pnl = pnl['daily_pl'][-1]
            pnl = pnl[pnl.pct_rank < 1-ci] # Find the tail distribution
            # self.Debug(daily_pnl)
            # The first parameter is PnL, the second parameter is the daily VaR
            return [daily_pnl, pnl['daily_pl'].max()]
        
    def adjusted_wt(self, w1, w2):
        # This function is to show how to calculate the new weight for reducing VaR. 
        # It is not being used in the trading. 
        
        # reduce portfolio weight to reduce var usage
        pos1 = round(self.equity*w1/self.px1)
        pos2 = round(self.equity*w2/self.px2)
    
        var = self.VarCalc(self.ci, pos1, pos2, self.dg )[1]
        adj = min(0, 1-var/self.var_limit) + 1
        
        #self.Debug ("Equity is: " + str(self.equity) + " VAR is: " +str(var)+ " wt1 "  + str(w1) +" wt2 "  + str(w2)+ " pos1 "  + str(pos1) +" pos2 "  + str(pos2) )
        if var <- self.var_limit:  # adjust the portfolio position size downward
            self.Debug (str(var) + " Position Adjusted Down by " + str(adj) )
        return [w1 * adj, w2 * adj]
    
    def record_daily_info(self, pairs, pos1, pos2, px1, px2):
        s = str(pairs[0] + ', ' + pairs[1])
        df = self.pair_pnl[s].copy()
        if df.shape[0] == 0:
            pnl = 0
        else:
            pos_1 = float(df['pos1'][-1])
            pos_2 = float(df['pos2'][-1])
            px_1 = float(df['px1'][-1])
            px_2 = float(df['px2'][-1])
            
            pnl = pos_1*(px1 - px_1) + pos_2*(px2 - px_2)
            
        new= pd.DataFrame({'pos1':pos1,
                  'pos2':pos2,
                  'px1':px1,
                  'px2':px2,
                  'PnL':pnl},
                 index=[self.Time]) 
        df=df.append(new,ignore_index= False)
        
        self.pair_pnl[s] = df
        
        
    # This function trades a pair, the method is OLS or Kalman Filter
    def pairs_trade(self, pairs, method):
        self.IsInvested = (self.Portfolio[pairs[0]].Invested) or (self.Portfolio[pairs[1]].Invested)
        self.ShortSpread = self.Portfolio[pairs[0]].IsShort
        self.LongSpread = self.Portfolio[pairs[0]].IsLong
        if method == 'Kalman':
            zscore = self.slope_kalman(pairs)[0]
            self.beta = self.slope_kalman(pairs)[1]
        if method == 'ols':
            zscore = self.port_check(pairs[0], pairs[1])[1][-1]
            self.beta = self.port_check(pairs[0], pairs[1])[2]
        
        self.wt1 = 1/(1+self.beta)
        self.wt2 = self.beta/(1+self.beta)
        
        self.pos1 = self.Portfolio[pairs[0]].Quantity
        self.px1 = self.Portfolio[pairs[0]].Price
        self.pos2 = self.Portfolio[pairs[1]].Quantity
        self.px2 = self.Portfolio[pairs[1]].Price
 
        self.equity =self.Portfolio.TotalPortfolioValue
        
        # Calculate the weights currently
        # self.wt1_already = (self.pos1 * self.px1)/self.equity
        # self.wt2_already = (self.pos2 * self.px2)/self.equity
        
        
        gross_mkv = abs(self.pos1) * self.px1 + abs(self.pos2) * self.px2
        gross_margin = gross_mkv * self.margin_pct
        
        margin = max(gross_margin, self.Portfolio.TotalMarginUsed)
        
        
        #self.Debug ("VAR Is: " +str(var) + ' Port Margin ' + str(self.Portfolio.TotalMarginUsed) + 'Gross Margin '+ str(gross_margin) )
        #self.Debug ("VAR Is: " +str(var) + ' Port_pos1 ' + str(self.pos1) +  ' Port_pos2 ' + str(self.pos2) )
        #self.Debug (self.dg.head(1))
        
        entry_condition = (self.equity > margin * (1 + self.margin_buffer))
        
        if self.IsInvested:
            if self.ShortSpread and zscore <= self.exit or \
                self.LongSpread and zscore >= -self.exit:
                    
                self.Liquidate(pairs[0])
                self.Liquidate(pairs[1])
                # if pairs[0] == 'DHR R735QTJ8XC9X':
                    # self.Debug(self.Portfolio[pairs[0]].Quantity)
                    # self.Debug(self.Portfolio[pairs[1]].Quantity)
                
        elif entry_condition:
            #[weight1, weight2] = self.adjusted_wt(weight1, weight2)
            if zscore > self.enter:
                self.SetHoldings(pairs[0], -self.wt1/self.num) 
                self.SetHoldings(pairs[1],  self.wt2/self.num)   
            if zscore < - self.enter:
                self.SetHoldings(pairs[0],  self.wt1/self.num)
                self.SetHoldings(pairs[1], -self.wt2/self.num)
        else:
            pass
        
        self.pos1 = self.Portfolio[self.pairs[0]].Quantity
        self.pos2 = self.Portfolio[self.pairs[1]].Quantity
        PnL_pair, var = self.VarCalc(pairs, self.ci, self.pos1, self.pos2, self.dg )
        
        # Adjustment based on VaR
        if self.pos1 !=0 and self.pos2 !=0:

            #compute portfolio VaR
            # var = self.VarCalc(self.ci, self.pos1, self.pos2, self.dg )[1]
            
            # figure out the adujustment factor based on the amount that var is over self.var_limit
            adj= 1/(max(0, -var/self.var_limit-1) +1)
            wt1_adj = self.wt1* (adj-1)
            wt2_adj = self.wt2* (adj-1)
            
            if adj< 1: #if the VaR limit is violated
            
                self.Debug ("Reducing Position to "+  str(adj) + " of target position due to VaR " + str(var) +' > VaR limit of ' +str(self.var_limit))
                
                #incrementally to reduce the position
                
                if self.ShortSpread:
                    self.SetHoldings(self.Symbol(pairs[0]), -wt1_adj)
                    self.SetHoldings(self.Symbol(pairs[1]), wt2_adj)
                else:
                    self.SetHoldings(self.Symbol(pairs[0]), wt1_adj)
                    self.SetHoldings(self.Symbol(pairs[1]), -wt2_adj)
        

        
        # for a certain pair, if the loss of this pair is more than the max_loss threshold per pair,
        # liquidate the positions of this pair
        
        # Positions after latest trading
        pos1 = self.Portfolio[pairs[0]].Quantity
        px1 = self.Portfolio[pairs[0]].Price
        pos2 = self.Portfolio[pairs[1]].Quantity
        px2 = self.Portfolio[pairs[1]].Price

        self.record_daily_info(pairs, pos1, pos2, px1, px2) 
        
        s = str(pairs[0] + ', ' + pairs[1])
        pnl_pair = self.pair_pnl[s].PnL.sum()
        
        if pnl_pair < -self.max_loss * self.cash / self.num or\
            self.ShortSpread and zscore >= self.stop_loss or\
            self.LongSpread and zscore <= -self.stop_loss:
            self.Liquidate(pairs[0])
            self.Liquidate(pairs[1])
            # We can decide whether we would like use this pair anymore.
            self.selected.remove(pairs)
            self.num = self.num - 1
            self.Debug("stop loss on pair of " + str(pairs[0]) +', ' + str(pairs[1]))
    # Gold Trading Strategy ############################################
    def Gold_Strategy(self):
        df_gold = self.History(self.gold_symbols, 100, Resolution.Daily)
        df1_gold = df_gold.loc["SPY"]
        df2_gold = df_gold.loc["SGOL"]
        # df3 = df.loc["DBP"]
        # df4 = df.loc["GLDM"]
        df_ratio = df1_gold/df2_gold
        ema = ta.trend.EMAIndicator(df_ratio['close'], self.window)
        if(df_ratio['close'][-1] > ema.ema_indicator()[-1]):
            # self.Liquidate("SGOL")
            self.SetHoldings("SPY", 0.1)
        if(df_ratio['close'][-1] < ema.ema_indicator()[-1]):
            # self.Liquidate("SPY")
            self.SetHoldings("SGOL", 0.1)   
    # Gold Trading Strategy ############################################
    


        
    def OnData(self, data):
        for pairs in self.selected:
            self.pairs = pairs
            self.pairs_trade(pairs,'Kalman')
            #self.Kalman_Trade(pairs)
        self.Gold_Strategy()
