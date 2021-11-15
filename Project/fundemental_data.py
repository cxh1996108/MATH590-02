# Your New Python File
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np

# from yahoofinancials import YahooFinancials
# 目前用這個 library 爬財報資料，再試試看IB怎麼用
# 這個爬的很慢
# 我覺得這個的價值比較在書面報告


def find_fundamental_df(start_number, end_number, tickers):
    ev_sales = []
    margins = []
    beta = []
    g = []
    col_names = []
    for i in tickers[start_number: end_number]:
        try:
            yahoo_financials = YahooFinancials(i)
            ev_sales.append(yahoo_financials.get_key_statistics_data()[
                            i]["enterpriseToRevenue"])
            margins.append(yahoo_financials.get_key_statistics_data()[
                i]["profitMargins"])
            beta.append(yahoo_financials.get_key_statistics_data()[i]['beta'])
            g.append(yahoo_financials.get_key_statistics_data()
                     [i]['earningsQuarterlyGrowth'])
            col_names.append(i)
        except:
            pass
    df = pd.DataFrame(
        {
            'ev_sales': ev_sales,
            'margins': margins,
            'beta': beta,
            'g': g,
        },
        index=col_names
    )
    df.columns = ['ticker', 'ev_sales', 'margins', 'beta', 'g']
    df.to_csv(f'df_{start_number +1}_to_{end_number + 1}.csv', index=True)
    return df
    
    
# 之前我是用 SP500, 500 種股票來爬，之後會用 'selected_pairs.py'裡的pair 來試

def find_tickers():
    df = pd.read_csv('SP500.csv')
    df.columns = df.iloc[0]
    df = df.drop([0])
    tickers = df['Symbol'].to_list()
    df.to_csv('tickers.csv', index=False)
    return tickers


df = pd.read_csv('full_df_1_to_500.csv')

# 為了控制不同產業做回歸，其他可以用的也有 p/e, PEG, ...  
def find_predicted_ev_sales(csvdata):
    mod = smf.ols( formula='ev_sales ~ margins + beta + g', data= csvdata)
    res = mod.fit()

# margins, beta 的係數也真的顯著

# OLS Regression Results                            
# ==============================================================================
# Dep. Variable:               ev_sales   R-squared:                       0.194
# Model:                            OLS   Adj. R-squared:                  0.188
# Method:                 Least Squares   F-statistic:                     32.60
# Date:                Mon, 19 Apr 2021   Prob (F-statistic):           6.70e-19
# Time:                        21:12:25   Log-Likelihood:                -1233.5
# No. Observations:                 410   AIC:                             2475.
# Df Residuals:                     406   BIC:                             2491.
# Df Model:                           3                                         
# Covariance Type:            nonrobust                                         
# ==============================================================================
#                  coef    std err          t      P>|t|      [0.025      0.975]
# ------------------------------------------------------------------------------
# Intercept      5.5693      0.713      7.814      0.000       4.168       6.970
# margins       14.4151      1.604      8.985      0.000      11.261      17.569
# beta          -1.4117      0.571     -2.474      0.014      -2.534      -0.290
# g             -0.0262      0.049     -0.540      0.590      -0.122       0.069
# ==============================================================================
# Omnibus:                      118.091   Durbin-Watson:                   2.157
# Prob(Omnibus):                  0.000   Jarque-Bera (JB):              332.949
# Skew:                           1.360   Prob(JB):                     5.02e-73
# Kurtosis:                       6.477   Cond. No.                         35.4
# ==============================================================================
