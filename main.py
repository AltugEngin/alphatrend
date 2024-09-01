import yfinance as yf
import pandas as pd
import pandas_ta as ta
from json import loads, dumps
from fastapi import FastAPI
app=FastAPI()
from BIST100 import stocks
#stocks=["YKBNK.IS","AEFES.IS","AVOD.IS"]



def alphaTrend(df):

    open = df['Open']
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    ap = 14
    tr = ta.true_range(high, low, close)
    atr = ta.sma(tr, ap)
    noVolumeData = False
    coeff = 1
    upt = []
    downT = []
    AlphaTrend = [0.0]
    src = close
    rsi = ta.rsi(src, 14)
    hlc3 = []
    k1 = []
    k2 = []
    tarih=[]
    mfi = ta.mfi(high, low, close, volume, 14)
    for i in range(len(close)):
        hlc3.append((high[i] + low[i] + close[i]) / 3)

    for i in range(len(low)):
        if pd.isna(atr[i]):
            upt.append(0)
        else:
            upt.append(low[i] - (atr[i] * coeff))
    for i in range(len(high)):
        if pd.isna(atr[i]):
            downT.append(0)
        else:
            downT.append(high[i] + (atr[i] * coeff))
    for i in range(1, len(close)):
        if noVolumeData is True and rsi[i] >= 50:
            if upt[i] < AlphaTrend[i - 1]:
                AlphaTrend.append(AlphaTrend[i - 1])
            else:
                AlphaTrend.append(upt[i])

        elif noVolumeData is False and mfi[i] >= 50:
            if upt[i] < AlphaTrend[i - 1]:
                AlphaTrend.append(AlphaTrend[i - 1])
            else:
                AlphaTrend.append(upt[i])
        else:
            if downT[i] > AlphaTrend[i - 1]:
                AlphaTrend.append(AlphaTrend[i - 1])
            else:
                AlphaTrend.append(downT[i])

    for i in range(len(AlphaTrend)):
        if i < 2:
            k2.append(0)
            k1.append(AlphaTrend[i])
        else:
            k2.append(AlphaTrend[i - 2])
            k1.append(AlphaTrend[i])

    at = pd.DataFrame(data=k1, columns=['k1'])
    at['k2'] = k2

    sinyalSirasi=['SELL']

    for i in range(1,at.shape[0]):
        if k1[i-1]<=k2[i-1] and k1[i]>k2[i] and sinyalSirasi[-1]!='BUY':
            sinyalSirasi.append('BUY')
            tarih.append(df.index[i])
        elif k1[i-1]>=k2[i-1] and k1[i]<k2[i] and sinyalSirasi[-1]!='SELL':
            sinyalSirasi.append('SELL')
            tarih.append(df.index[i])
    del(sinyalSirasi[0])
    result=pd.DataFrame(data=[tarih,sinyalSirasi])
    res1=result.drop(result.columns[0],axis=1)
    #print(res1.to_string())
    return res1

def allStocks(stocks):
    stock = yf.Ticker(stocks)
    pd_stock = pd.DataFrame(stock.history(period="1y"))
    new=alphaTrend(df=pd_stock)
    new['Stock']=stocks
    return new

allStocks_json=""

for x in stocks:
    try:
        result = allStocks(x).iloc[:,-2:].to_json(orient="values",date_format="iso")
        parsed = loads(result)
        allStocks_json+=dumps(parsed, indent=None)
        print(allStocks(x).iloc[:,-2:])
    except:
        print("error")
    else:
        pass



@app.get("/stocks")
async def read_root():
    return allStocks_json