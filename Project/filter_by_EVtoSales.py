# from selected_paris import selected
# import numpy as np
# import statsmodels.formula.api as smf
# import statsmodels.api as sm
# import pandas as pd
# from yahoofinancials import YahooFinancials
# import seaborn as sns
# import matplotlib.pyplot as plt


# # %%
# def find_fundamental_df(start_number, end_number, tickers):
#     ev_sales = []
#     margins = []
#     beta = []
#     g = []
#     col_names = []
#     for i in tickers[start_number: end_number]:
#         try:
#             yahoo_financials = YahooFinancials(i)
#             ev_sales.append(yahoo_financials.get_key_statistics_data()[
#                             i]["enterpriseToRevenue"])
#             margins.append(yahoo_financials.get_key_statistics_data()[
#                 i]["profitMargins"])
#             beta.append(yahoo_financials.get_key_statistics_data()[i]['beta'])
#             g.append(yahoo_financials.get_key_statistics_data()
#                      [i]['earningsQuarterlyGrowth'])
#             col_names.append(i)
#         except:
#             pass
#     df = pd.DataFrame(
#         {
#             'ev_sales': ev_sales,
#             'margins': margins,
#             'beta': beta,
#             'g': g,
#         },
#         index=col_names
#     )

#     df.to_csv(f'df_{start_number +1}_to_{end_number + 1}.csv', index=True)
#     df.columns = ['ticker', 'ev_sales', 'margins', 'beta', 'g']

#     return df


# def find_tickers():
#     df = pd.read_csv('SP500.csv')
#     df.columns = df.iloc[0]
#     df = df.drop([0])
#     tickers = df['Symbol'].to_list()
#     df.to_csv('tickers.csv', index=False)
#     return tickers


# # %%
# def find_predicted_ev_sales_model(csvdata):
#     mod = smf.ols(formula='ev_sales ~ margins + beta + g', data=csvdata)
#     res = mod.fit()
#     return res


# def clean_tickers(selected):
#     tickers_from_clustering = []
#     for i in selected:
#         current_0 = i[0].split(' ')[0]
#         current_1 = i[1].split(' ')[0]
#         current_pair = [current_0, current_1]
#         tickers_from_clustering.append(current_pair)
#     return tickers_from_clustering


# def find_clean_tickers_set(tickers_from_clustering):
#     tickers_selected = clean_tickers(tickers_from_clustering)
#     flattened = [val for sublist in tickers_selected for val in sublist]
#     return flattened


# def find_undervalued_set(df):
#     ev_predicting_model = find_predicted_ev_sales_model(df)
#     df['fitted_values'] = ev_predicting_model.fittedvalues

#     df_undervalued = df[df['ev_sales'] < df['fitted_values']]
#     undervalued_set = set(df_undervalued['ticker'])
#     return(undervalued_set)


# def find_selected_SP500(selected_pair_cleaned, SP500_tickers):
#     SP500_pair = []
#     for pair in selected_pair_cleaned:
#         if set(pair) <= set(SP500_tickers):
#             SP500_pair.append(pair)
#     return SP500_pair


# def find_selected_SP500_undervalued_pair(SP500_pair, undervalued_set):
#     SP500_pair_undervalued = []
#     for pair in SP500_pair:
#         if len(set(pair).intersection(undervalued_set)) == 2:
#             SP500_pair_undervalued.append(pair)
#     return SP500_pair_undervalued


# def find_dict_selected(selected, selected_clean):

#     tickers_from_clustering = []
#     for i in range(0, len(selected)):
#         dic = dict(zip(selected_clean[i], selected[i]))
#         tickers_from_clustering.append(dic)
#     return tickers_from_clustering


# def find_final_ticker(dict_selected, selected_SP500_pair_undervalued):
#     final_tickers = []
#     for i in range(0, len(dict_selected)):
#         for ticker in selected_SP500_pair_undervalued:
#             if ticker[0] in dict_selected[i].keys() and ticker[1] in dict_selected[i].keys():
#                 final_tickers.append(
#                     [dict_selected[i][ticker[0]], dict_selected[i][ticker[1]]])
#     return final_tickers


# # %%
# SP500_tickers = find_tickers()
# df = pd.read_csv('full_df_1_to_500.csv')
# ev_model = find_predicted_ev_sales_model(df)

# # %%
# selected_clean = clean_tickers(selected)
# selected_set = find_clean_tickers_set(selected_clean)

# # %%
# undervalued_set = find_undervalued_set(df)
# selected_SP500_pair = find_selected_SP500(selected_clean, SP500_tickers)

# # %%
# selected_SP500_pair_undervalued = find_selected_SP500_undervalued_pair(
#     selected_SP500_pair, undervalued_set)

# # %%
# dict_selected = find_dict_selected(selected, selected_clean)
# final_tickers = find_final_ticker(
#     dict_selected, selected_SP500_pair_undervalued)

# print(final_tickers)



# # by fundamental data 
# further_selected = [
#  ['AJG R735QTJ8XC9X', 'MMC R735QTJ8XC9X'],
#  ['LNC R735QTJ8XC9X', 'PRU SAI0XJNH6IJP'],
#  ['AEE R735QTJ8XC9X', 'AEP R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'DTE R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'ED R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'CMS R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'ED R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['CMS R735QTJ8XC9X', 'ED R735QTJ8XC9X'],
#  ['CMS R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['CMS R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['DTE R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['DTE R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['ED R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['ED R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['ETR R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['IP R735QTJ8XC9X', 'WRK W1V0C8ZTUBTX'],
#  ['DHI R735QTJ8XC9X', 'LEN R735QTJ8XC9X'],
#  ['DHI R735QTJ8XC9X', 'PHM R735QTJ8XC9X']
#  ]# from selected_paris import selected
# import numpy as np
# import statsmodels.formula.api as smf
# import statsmodels.api as sm
# import pandas as pd
# from yahoofinancials import YahooFinancials
# import seaborn as sns
# import matplotlib.pyplot as plt


# # %%
# def find_fundamental_df(start_number, end_number, tickers):
#     ev_sales = []
#     margins = []
#     beta = []
#     g = []
#     col_names = []
#     for i in tickers[start_number: end_number]:
#         try:
#             yahoo_financials = YahooFinancials(i)
#             ev_sales.append(yahoo_financials.get_key_statistics_data()[
#                             i]["enterpriseToRevenue"])
#             margins.append(yahoo_financials.get_key_statistics_data()[
#                 i]["profitMargins"])
#             beta.append(yahoo_financials.get_key_statistics_data()[i]['beta'])
#             g.append(yahoo_financials.get_key_statistics_data()
#                      [i]['earningsQuarterlyGrowth'])
#             col_names.append(i)
#         except:
#             pass
#     df = pd.DataFrame(
#         {
#             'ev_sales': ev_sales,
#             'margins': margins,
#             'beta': beta,
#             'g': g,
#         },
#         index=col_names
#     )

#     df.to_csv(f'df_{start_number +1}_to_{end_number + 1}.csv', index=True)
#     df.columns = ['ticker', 'ev_sales', 'margins', 'beta', 'g']

#     return df


# def find_tickers():
#     df = pd.read_csv('SP500.csv')
#     df.columns = df.iloc[0]
#     df = df.drop([0])
#     tickers = df['Symbol'].to_list()
#     df.to_csv('tickers.csv', index=False)
#     return tickers


# # %%
# def find_predicted_ev_sales_model(csvdata):
#     mod = smf.ols(formula='ev_sales ~ margins + beta + g', data=csvdata)
#     res = mod.fit()
#     return res


# def clean_tickers(selected):
#     tickers_from_clustering = []
#     for i in selected:
#         current_0 = i[0].split(' ')[0]
#         current_1 = i[1].split(' ')[0]
#         current_pair = [current_0, current_1]
#         tickers_from_clustering.append(current_pair)
#     return tickers_from_clustering


# def find_clean_tickers_set(tickers_from_clustering):
#     tickers_selected = clean_tickers(tickers_from_clustering)
#     flattened = [val for sublist in tickers_selected for val in sublist]
#     return flattened


# def find_undervalued_set(df):
#     ev_predicting_model = find_predicted_ev_sales_model(df)
#     df['fitted_values'] = ev_predicting_model.fittedvalues

#     df_undervalued = df[df['ev_sales'] < df['fitted_values']]
#     undervalued_set = set(df_undervalued['ticker'])
#     return(undervalued_set)


# def find_selected_SP500(selected_pair_cleaned, SP500_tickers):
#     SP500_pair = []
#     for pair in selected_pair_cleaned:
#         if set(pair) <= set(SP500_tickers):
#             SP500_pair.append(pair)
#     return SP500_pair


# def find_selected_SP500_undervalued_pair(SP500_pair, undervalued_set):
#     SP500_pair_undervalued = []
#     for pair in SP500_pair:
#         if len(set(pair).intersection(undervalued_set)) == 2:
#             SP500_pair_undervalued.append(pair)
#     return SP500_pair_undervalued


# def find_dict_selected(selected, selected_clean):

#     tickers_from_clustering = []
#     for i in range(0, len(selected)):
#         dic = dict(zip(selected_clean[i], selected[i]))
#         tickers_from_clustering.append(dic)
#     return tickers_from_clustering


# def find_final_ticker(dict_selected, selected_SP500_pair_undervalued):
#     final_tickers = []
#     for i in range(0, len(dict_selected)):
#         for ticker in selected_SP500_pair_undervalued:
#             if ticker[0] in dict_selected[i].keys() and ticker[1] in dict_selected[i].keys():
#                 final_tickers.append(
#                     [dict_selected[i][ticker[0]], dict_selected[i][ticker[1]]])
#     return final_tickers


# # %%
# SP500_tickers = find_tickers()
# df = pd.read_csv('full_df_1_to_500.csv')
# ev_model = find_predicted_ev_sales_model(df)

# # %%
# selected_clean = clean_tickers(selected)
# selected_set = find_clean_tickers_set(selected_clean)

# # %%
# undervalued_set = find_undervalued_set(df)
# selected_SP500_pair = find_selected_SP500(selected_clean, SP500_tickers)

# # %%
# selected_SP500_pair_undervalued = find_selected_SP500_undervalued_pair(
#     selected_SP500_pair, undervalued_set)

# # %%
# dict_selected = find_dict_selected(selected, selected_clean)
# final_tickers = find_final_ticker(
#     dict_selected, selected_SP500_pair_undervalued)

# print(final_tickers)



# # by fundamental data 
# further_selected = [
#  ['AJG R735QTJ8XC9X', 'MMC R735QTJ8XC9X'],
#  ['LNC R735QTJ8XC9X', 'PRU SAI0XJNH6IJP'],
#  ['AEE R735QTJ8XC9X', 'AEP R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'DTE R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'ED R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['AEE R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'CMS R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'ED R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['AEP R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['CMS R735QTJ8XC9X', 'ED R735QTJ8XC9X'],
#  ['CMS R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['CMS R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['DTE R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['DTE R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['ED R735QTJ8XC9X', 'ETR R735QTJ8XC9X'],
#  ['ED R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['ETR R735QTJ8XC9X', 'WEC R735QTJ8XC9X'],
#  ['IP R735QTJ8XC9X', 'WRK W1V0C8ZTUBTX'],
#  ['DHI R735QTJ8XC9X', 'LEN R735QTJ8XC9X'],
#  ['DHI R735QTJ8XC9X', 'PHM R735QTJ8XC9X']
#  ]
