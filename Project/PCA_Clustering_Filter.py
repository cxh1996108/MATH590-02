from sklearn.cluster import DBSCAN
from sklearn.cluster import OPTICS, cluster_optics_dbscan
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import preprocessing
from statsmodels.tsa.stattools import coint
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import sys
import math
import warnings
qb = QuantBook()
#In sample period
screening_time = datetime(2016,1,1) # This is the latest listing date for stocks to be seletced
start_time = datetime(2018, 1, 2) # start datetime for history call
end_time = datetime(2021, 4, 15) # end datetime for history call
# CCS
'''
tickers = ['AACG','ACH','AEHL','AGBA','AGBAU','AGMH','AIH','AIHS','AMBO','ANPC',
 'API','APM','ATCO','ATHM','ATIF','BABA','BAOS','BEDU','BEKE','BEST','BGNE','BHAT',
 'BIDU','BILI','BIMI','BLCT','BNR','BQ','BRQS','BTBT','BYSI','BZUN','CAAS','CAN',
 'CANG','CBAT','CCM','CCNC','CCRC','CD','CEA','CGA','CHNR','CIH','CJJD','CLEU','CLPS',
 'CLWT','CMCM','CNET','CNEY','CNF','CNTB','CO','COE','CPHI','CREG','CSCW','CSIQ','CTK','CXDC','CYD',
 'DADA','DAO','DOGZ','DOYU','DQ','DSWL','DTSS','DUO','DXF','EBON','EDTK','EDU','EH','EM','EVK',
 'EZGO','FAMI','FANH','FEDU','FENG','FFHL','FHS','FINV','FTFT','FUTU','GDS','GHG','GLG','GSMG',
 'GSX','GTEC','GTH','GURE','HAPP','HCM','HGSH','HIHO','HLG','HNP','HOLI','HTHT','HUDI','HUIZ',
 'HUSN','HUYA','HX','HYW','ICLK','IDEX','IFBD','IH','IMAB','IQ','ITP','JD','JFIN','JFU','JG','JKS',
 'JOBS','JP','JRJC','JT','JWEL','KBSF','KC','KNDI','KRKR','KUKE','KXIN','LAIX','LEGN','LEJU','LFC',
 'LGHL','LI','LITB','LIZI','LKCO','LLIT','LU','LX','LXEH','LYL','MARK','MDJH','METX','MFH','MKD','MLCO',
 'MNSO','MOGU','MOHO','MOMO','MOXC','MSC','MTC','MYT','NCTY','NEW','NEWA','NFH','NIO','NISN','NIU',
 'NOAH','NTES','NTP','NVFY','NVVE','OCFT','OCG','OIIM','ONE','OSN','PBTS','PDD','PETZ','PHCF','PLAG',
 'PLIN','PME','PT','PTR','PUYI','QD','QFIN','QH','QK','QLI','QTT','RCON','REDU','RENN','RETO',
 'RLX','RYB','SDH','SECO','SEED','SFUN','SGOC','SHI','SINO','SJ','SNP','SOGO','SOHU','SOL','SOS',
 'SPI','STG','SVA','SVM','SXTC','SY','TAL','TANH','TAOP','TC','TCOM','TEDU','TIGR','TIRX','TKAT','TME',
 'TOUR','TSP','TYHT','UCL','UPC','UTME','UTSI','UXIN','VIOT','VIPS','VNET','WAFU','WB',
 'WEI','WIMI','WNW','XIN','XNET','XPEV','XYF','YGMZ','YI','YJ','YQ','YRD','YSG','YUMC','YY','ZCMD',
 'ZGYH','ZGYHU','ZKIN','ZLAB','ZNH','ZTO']
'''
# ETF
#tickers = ["SPY","IVV","VTI","VOO","QQQ","VEA","IEFA","AGG","IEMG","VWO","VTV","BND","IWM","VUG","IJR","IWF","IJH","GLD","VIG","EFA","IWD","VO","VB","VXUS","VCIT","LQD","VGT","BNDX","XLF","XLK","VCSH","VNQ","ITOT","VYM","VEU","BSV","IVW","EEM","USMV","DIA","IAU","SCHX","IWR","IWB","IXUS","MBB","TIP","SCHF","XLV","RSP","IGSB","XLE","VBR","VV","IVE","SCHD","ARKK","MUB","HYG","MDY","SHY","QUAL","XLI","SCHB","VT","XLY","SDY","PFF","DVY","EMB","DGRO","SCHP","IWN","JPST","SHV","ACWI","VGK","VXF","ESGU","SCHA","VBK","TLT","MINT","IWP","SLV","GOVT","IEF","BIV","VLUE","VMBS","VHT","MTUM","GDX","SCZ","SCHG","VOE","IWS","EWJ","BIL","XLC"]

# S&P500 components
tickers = ["MMM"	,"AOS"	,"ABT"	,"ABBV"	,"ABMD"	,"ACN"	,"ATVI"	,"ADBE"	,"AAP"	,"AMD"	,"AES"	,"AFL"	,"A"	,"APD"	,"AKAM"	,"ALK"	,"ALB"	,"ARE"	,"ALXN"	,"ALGN"	,"ALLE"	,"LNT"	,"ALL"	,"GOOGL"	,"GOOG"	,"MO"	,"AMZN"	,"AMCR"	,"AEE"	,"AAL"	,"AEP"	,"AXP"	,"AIG"	,"AMT"	,"AWK"	,"AMP"	,"ABC"	,"AME"	,"AMGN"	,"APH"	,"ADI"	,"ANSS"	,"ANTM"	,"AON"	,"APA"	,"AAPL"	,"AMAT"	,"APTV"	,"ADM"	,"ANET"	,"AJG"	,"AIZ"	,"T"	,"ATO"	,"ADSK"	,"ADP"	,"AZO"	,"AVB"	,"AVY"	,"BKR"	,"BLL"	,"BAC"	,"BAX"	,"BDX"	,"BRK.B"	,"BBY"	,"BIO"	,"BIIB"	,"BLK"	,"BA"	,"BKNG"	,"BWA"	,"BXP"	,"BSX"	,"BMY"	,"AVGO"	,"BR"	,"BF.B"	,"CHRW"	,"COG"	,"CDNS"	,"CZR"	,"CPB"	,"COF"	,"CAH"	,"KMX"	,"CCL"	,"CARR"	,"CTLT"	,"CAT"	,"CBOE"	,"CBRE"	,"CDW"	,"CE"	,"CNC"	,"CNP"	,"CERN"	,"CF"	,"SCHW"	,"CHTR"	,"CVX"	,"CMG"	,"CB"	,"CHD"	,"CI"	,"CINF"	,"CTAS"	,"CSCO"	,"C"	,"CFG"	,"CTXS"	,"CME"	,"CMS"	,"KO"	,"CTSH"	,"CL"	,"CMCSA"	,"CMA"	,"CAG"	,"COP"	,"ED"	,"STZ"	,"CPRT"	,"GLW"	,"CTVA"	,"COST"	,"CCI"	,"CSX"	,"CMI"	,"CVS"	,"DHI"	,"DHR"	,"DRI"	,"DVA"	,"DE"	,"DAL"	,"XRAY"	,"DVN"	,"DXCM"	,"FANG"	,"DLR"	,"DFS"	,"DISCA"	,"DISCK"	,"DISH"	,"DG"	,"DLTR"	,"D"	,"DPZ"	,"DOV"	,"DOW"	,"DTE"	,"DUK"	,"DRE"	,"DD"	,"DXC"	,"EMN"	,"ETN"	,"EBAY"	,"ECL"	,"EIX"	,"EW"	,"EA"	,"EMR"	,"ENPH"	,"ETR"	,"EOG"	,"EFX"	,"EQIX"	,"EQR"	,"ESS"	,"EL"	,"ETSY"	,"RE"	,"EVRG"	,"ES"	,"EXC"	,"EXPE"	,"EXPD"	,"EXR"	,"XOM"	,"FFIV"	,"FB"	,"FAST"	,"FRT"	,"FDX"	,"FIS"	,"FITB"	,"FRC"	,"FE"	,"FISV"	,"FLT"	,"FLIR"	,"FMC"	,"F"	,"FTNT"	,"FTV"	,"FBHS"	,"FOXA"	,"FOX"	,"BEN"	,"FCX"	,"GPS"	,"GRMN"	,"IT"	,"GNRC"	,"GD"	,"GE"	,"GIS"	,"GM"	,"GPC"	,"GILD"	,"GPN"	,"GL"	,"GS"	,"GWW"	,"HAL"	,"HBI"	,"HIG"	,"HAS"	,"HCA"	,"PEAK"	,"HSIC"	,"HES"	,"HPE"	,"HLT"	,"HFC"	,"HOLX"	,"HD"	,"HON"	,"HRL"	,"HST"	,"HWM"	,"HPQ"	,"HUM"	,"HBAN"	,"HII"	,"IEX"	,"IDXX"	,"INFO"	,"ITW"	,"ILMN"	,"INCY"	,"IR"	,"INTC"	,"ICE"	,"IBM"	,"IFF"	,"IP"	,"IPG"	,"INTU"	,"ISRG"	,"IVZ"	,"IPGP"	,"IQV"	,"IRM"	,"JBHT"	,"JKHY"	,"J"	,"SJM"	,"JNJ"	,"JCI"	,"JPM"	,"JNPR"	,"KSU"	,"K"	,"KEY"	,"KEYS"	,"KMB"	,"KIM"	,"KMI"	,"KLAC"	,"KHC"	,"KR"	,"LB"	,"LHX"	,"LH"	,"LRCX"	,"LW"	,"LVS"	,"LEG"	,"LDOS"	,"LEN"	,"LLY"	,"LNC"	,"LIN"	,"LYV"	,"LKQ"	,"LMT"	,"L"	,"LOW"	,"LUMN"	,"LYB"	,"MTB"	,"MRO"	,"MPC"	,"MKTX"	,"MAR"	,"MMC"	,"MLM"	,"MAS"	,"MA"	,"MXIM"	,"MKC"	,"MCD"	,"MCK"	,"MDT"	,"MRK"	,"MET"	,"MTD"	,"MGM"	,"MCHP"	,"MU"	,"MSFT"	,"MAA"	,"MHK"	,"TAP"	,"MDLZ"	,"MPWR"	,"MNST"	,"MCO"	,"MS"	,"MSI"	,"MSCI"	,"NDAQ"	,"NTAP"	,"NFLX"	,"NWL"	,"NEM"	,"NWSA"	,"NWS"	,"NEE"	,"NLSN"	,"NKE"	,"NI"	,"NSC"	,"NTRS"	,"NOC"	,"NLOK"	,"NCLH"	,"NOV"	,"NRG"	,"NUE"	,"NVDA"	,"NVR"	,"NXPI"	,"ORLY"	,"OXY"	,"ODFL"	,"OMC"	,"OKE"	,"ORCL"	,"OTIS"	,"PCAR"	,"PKG"	,"PH"	,"PAYX"	,"PAYC"	,"PYPL"	,"PENN"	,"PNR"	,"PBCT"	,"PEP"	,"PKI"	,"PRGO"	,"PFE"	,"PM"	,"PSX"	,"PNW"	,"PXD"	,"PNC"	,"POOL"	,"PPG"	,"PPL"	,"PFG"	,"PG"	,"PGR"	,"PLD"	,"PRU"	,"PEG"	,"PSA"	,"PHM"	,"PVH"	,"QRVO"	,"QCOM"	,"PWR"	,"DGX"	,"RL"	,"RJF"	,"RTX"	,"O"	,"REG"	,"REGN"	,"RF"	,"RSG"	,"RMD"	,"RHI"	,"ROK"	,"ROL"	,"ROP"	,"ROST"	,"RCL"	,"SPGI"	,"CRM"	,"SBAC"	,"SLB"	,"STX"	,"SEE"	,"SRE"	,"NOW"	,"SHW"	,"SPG"	,"SWKS"	,"SNA"	,"SO"	,"LUV"	,"SWK"	,"SBUX"	,"STT"	,"STE"	,"SYK"	,"SIVB"	,"SYF"	,"SNPS"	,"SYY"	,"TMUS"	,"TROW"	,"TTWO"	,"TPR"	,"TGT"	,"TEL"	,"TDY"	,"TFX"	,"TER"	,"TSLA"	,"TXN"	,"TXT"	,"BK"	,"CLX"	,"COO"	,"HSY"	,"MOS"	,"TRV"	,"DIS"	,"TMO"	,"TJX"	,"TSCO"	,"TT"	,"TDG"	,"TRMB"	,"TFC"	,"TWTR"	,"TYL"	,"TSN"	,"USB"	,"UDR"	,"ULTA"	,"UAA"	,"UA"	,"UNP"	,"UAL"	,"UPS"	,"URI"	,"UNH"	,"UHS"	,"UNM"	,"VLO"	,"VAR"	,"VTR"	,"VRSN"	,"VRSK"	,"VZ"	,"VRTX"	,"VFC"	,"VIAC"	,"VTRS"	,"V"	,"VNO"	,"VMC"	,"WRB"	,"WBA"	,"WMT"	,"WM"	,"WAT"	,"WEC"	,"WFC"	,"WELL"	,"WST"	,"WDC"	,"WU"	,"WAB"	,"WRK"	,"WY"	,"WHR"	,"WMB"	,"WLTW"	,"WYNN"	,"XEL"	,"XLNX"	,"XYL"	,"YUM"	,"ZBRA"	,"ZBH"	,"ZION"	,"ZTS"]
Get History Data
# Get history data of tickers with listing date before 2016/1/1
for ticker in tickers:
    qb.AddEquity(ticker, Resolution.Daily)
qb = QuantBook()

symbols = []
for ticker in tickers:
    symbol = qb.Symbol(ticker)
    date = symbol.ID.Date  
    if date < screening_time:
        qb.AddEquity(ticker, Resolution.Daily)
        symbols.append(symbol)  
            
history = qb.History(qb.Securities.Keys, start_time, end_time, Resolution.Daily)
df = history['close'].unstack(level=0)
# calculate daily return
dpct = df.pct_change().dropna()
dpct
Functions to Be Used Later
# Use PCA to reduce the demension of features
def pca(dpct,N_PRIN_COMPONENTS = 50):
    pca = PCA(n_components=N_PRIN_COMPONENTS)
    pca.fit(dpct)
    df_pca = pd.DataFrame(index = dpct.T.index, data = pca.components_.T)
    return df_pca
# DBSCAN to cluster tickers
def dbscan(df_pca,eps=0.15,min_samples=3):
    clf = DBSCAN(eps=eps,min_samples=min_samples)
    clf.fit(df_pca)
    labels = clf.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0) # eliminate noisy samples
    print("Clusters discovered by DBSCAN: %d" % n_clusters_)
    clustered_series_all = pd.Series(index=df_pca.index, data=labels.flatten())
    clustered_series = clustered_series_all[clustered_series_all != -1]
    counts = clustered_series.value_counts()
    print("Pairs to evaluate by DBSCAN: %d" % (counts * (counts - 1) / 2).sum())
    return  clustered_series_all, clustered_series, counts, clf
# OPTICS to cluster tickers
def optics(df_pca):
    clf_op = OPTICS(min_samples=3, metric='euclidean', cluster_method='xi')
    clf_op.fit(df_pca)
    labels_op = clf_op.labels_
    n_clusters_op = len(set(labels_op)) - (1 if -1 in labels_op else 0) # eliminate noisy samples
    print("Clusters discovered by OPTICS: %d" % n_clusters_op)
    clustered_series_all_op = pd.Series(index=df_pca.index, data=labels_op.flatten())
    clustered_series_op = clustered_series_all_op[clustered_series_all_op != -1]
    counts_op = clustered_series_op.value_counts()
    print("Pairs to evaluate by OPTICS: %d" % (counts_op * (counts_op - 1) / 2).sum())
    return clustered_series_all_op, clustered_series_op, counts_op, clf_op
# Show clusters‘ size
def cluster_size(series,method):
    plt.figure()
    plt.barh(
    range(len(series.value_counts())), # cluster labels, y axis
    series.value_counts()
    )
    plt.title('Cluster Member Counts by ' + method)
    plt.xlabel('Stocks in Cluster')
    plt.ylabel('Cluster Id');
# Visualize clustering result with t-SNE
def plot_TSNE(X, clf, clustered_series_all, method):
    """
    This function makes use of t-sne to visualize clusters in 2d.
    """
    
    X_tsne = TSNE(learning_rate=1000, perplexity=25, random_state=1337).fit_transform(X)
    
    # visualization
    fig = plt.figure(1, facecolor='white', figsize=(8,8), frameon=True, edgecolor='black')
    plt.clf()
    
    # axis in the middle
    ax = fig.add_subplot(1, 1, 1, alpha=0.9)
    # Move left y-axis and bottim x-axis to centre, passing through (0,0)
    ax.spines['left'].set_position('center')
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_position('center')
    ax.spines['bottom'].set_alpha(0.3)
    # Eliminate upper and right axes
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    # Show ticks in the left and lower axes only
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(which='major', labelsize=18)
    plt.axis('off')

    # etfs in cluster
    labels = clf.labels_
    x = X_tsne[(labels!=-1), 0]
    y = X_tsne[(labels!=-1), 1]
    tickers = list(clustered_series_all[clustered_series_all != -1].index)
    plt.scatter(
        x,
        y,
        s=100,
        alpha=0.95,
        c=labels[labels!=-1],
        cmap=cm.Paired
    )
    #for i, ticker in enumerate(tickers):
        #plt.annotate(ticker, (x[i]-20, y[i]+12), size=15)

    # remaining etfs, not clustered
    x = X_tsne[(clustered_series_all==-1).values, 0]
    y = X_tsne[(clustered_series_all==-1).values, 1]
    
    ''''
    tickers = list(clustered_series_all[clustered_series_all == -1].index)
    # WARNING: elimintate outliers
    outliers = ['TWTR VLE97YS7S57P','CPRT R735QTJ8XC9X']
    to_remove_x = [x[clustered_series_all[clustered_series_all==-1].index.get_loc(outliers[0])],
                   x[clustered_series_all[clustered_series_all==-1].index.get_loc(outliers[1])]]
    to_remove_y = [y[clustered_series_all[clustered_series_all==-1].index.get_loc(outliers[0])],
                   y[clustered_series_all[clustered_series_all==-1].index.get_loc(outliers[1])]]
    x = np.array([i for i in x if i not in to_remove_x])
    y= np.array([i for i in y if i not in to_remove_y])
    '''
    plt.scatter(
        x,
        y,
        s=100,
        alpha=0.1,
    )
    #for i, ticker in enumerate(tickers):
       #plt.annotate(ticker, (x[i], y[i]))#, arrowprops={'arrowstyle':'simple'})
        
    plt.title('T-SNE of all Stocks with ' + method + ' Clusters Noted', size =18)
    plt.xlabel('t-SNE Dim. 1', position=(0.92,0), size=12)
    plt.ylabel('t-SNE Dim. 2', position=(0,0.92), size=12)
    ax.set_xticks(range(-300, 300, 600))
    ax.set_yticks(range(-300, 300, 600))
    
    plt.show()
# Plot the log price series of stocks in each cluster
def plot_pairs(counts_op, clustered_series_op, df):
    warnings.filterwarnings('ignore')
    for clust in range(len(counts_op)):
        symbols = list(clustered_series_op[clustered_series_op==clust].index)
        means = np.log(df[symbols].mean())
        series = np.log(df[symbols]).sub(means)
        series.plot(figsize=(10,5))
# Plot the log price series of stocks in each cluster
def plot_pairs(counts_op, clustered_series_op, df):
    warnings.filterwarnings('ignore')
    for clust in range(len(counts_op)):
        symbols = list(clustered_series_op[clustered_series_op==clust].index)
        means = np.log(df[symbols].mean())
        series = np.log(df[symbols]).sub(means)
        series.plot(figsize=(10,5))
# Correlation test
def corr(pairs):
    i = 0
    corrs = []
    s_pair = []
    for pair in pairs:
        df = dict()
        i = i+1
        a = pair[0]
        c = qb.AddEquity(a)
        b = pair[1]
        d = qb.AddEquity(b)
        series1 = qb.History(c.Symbol,start_time, end_time, Resolution.Daily)
        series2 = qb.History(d.Symbol, start_time, end_time, Resolution.Daily)
        m = pd.Series(series1['close'].values)
        n = pd.Series(series2['close'].values)
        corr=m.corr(n,method='pearson')
        corrs.append(corr)
        s_pair.append(pair)
    ranks =pd.DataFrame({'pairs':s_pair,'corr':corrs})
    ranks.sort_values(by="corr" , inplace=True, ascending=False)
    #return ranks.head()
    return ranks[0:10]
# Cointegration test
def coin(pairs):
    i = 0
    coin = []
    s_pair = []
    for pair in pairs:
        df = dict()
        i = i+1
        a = pair[0]
        c = qb.AddEquity(a)
        b = pair[1]
        d = qb.AddEquity(b)
        series1 = qb.History(c.Symbol, start_time, end_time, Resolution.Daily)
        series2 = qb.History(d.Symbol, start_time, end_time, Resolution.Daily)
        m = pd.Series(series1['close'].values).apply(lambda x: math.log(x))
        n = pd.Series(series2['close'].values).apply(lambda x: math.log(x))
        coins = coint(m.values,n.values)
        coin.append(coins[1])
        s_pair.append(pair)
    ranks =pd.DataFrame({'pairs':s_pair,'coin':coin})
    ranks.sort_values(by="coin" , inplace=True, ascending=True)
    #return ranks.head()
    return ranks[0:10]
def pairs_to_list(df_pairs):
    pairs_list = []
    for pair in df_pairs['pairs']:
        pairs_list.append(pair)
    return pairs_list
Run This Part to Get the Output
