import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr
pd.options.plotting.backend = "plotly"
import plotly.graph_objects as go



# 기초변수 설정 ######################################
n_days = 365 * 3
now = datetime.now().date() + timedelta(days=1)
ago = now - timedelta(days=n_days)

ticker_pref = "005935"
ticker_comm = "005930"

######################################################


# @st.cache_data
def read_price(preferred, common, start, end):
    '''
    우선주티커, 본주티커, 불러오기 시작일자
    '''
    preferred = fdr.DataReader(preferred, start=start, end=end)[['Open', 'High', 'Low', 'Close']]
    preferred["OHLC_avg"] = (preferred.Open + preferred.High + preferred.Low + preferred.Close) / 4
    common = fdr.DataReader(common, start=start, end=end)[['Open', 'High', 'Low', 'Close']]
    common["OHLC_avg"] = (common.Open + common.High + common.Low + common.Close) / 4

    ratio = preferred / common

    return ratio

df = read_price(ticker_pref, ticker_comm, start=ago, end=now)



st.title("삼성전자우/삼성전자 페어")


st.markdown("---")   # 구분 가로선


st.subheader("삼성전자우/삼성전자 가격비율 추이")
st.write('''
    개별종목의 시가와 종가 시점의 비율임 (고가와 저가는 시차가 발생하므로 제외)   
    마우스 드래그 : 확대 / 더블클릭 : 축소
    '''
    )

fig = go.Figure(data=[go.Candlestick(
    increasing_line_color= 'red', decreasing_line_color= 'blue',
    x=df.index,
    open=df['Open'], 
    high=df['Open'],
    low=df['Open'], 
    close=df['Close']
)])
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig)



# 전광판
from_day = now - timedelta(days=5)
price_pref = fdr.DataReader(ticker_pref, start=from_day)["Close"]
price_comm = fdr.DataReader(ticker_comm, start=from_day)["Close"]
ratio_last = price_pref / price_comm

col1, col2, col3 = st.columns(3)

col1.metric("우선주", f"{price_pref[-1]}원", round(price_pref[-1] - price_pref[-2]))
col2.metric("본주", f"{price_comm[-1]}원", round(price_comm[-1] - price_comm[-2]))
col3.metric("비율", f"{round(ratio_last[-1], ndigits=4)}", round(ratio_last[-1] - ratio_last[-2], ndigits=4))


st.markdown("---")   # 구분 가로선




st.subheader("기간별 가격비율 요약")

# 아래 고점 저점은 시고저종이 아니라 기간 관측값에서 고점저점임  <-- 매우중요
def get_summ(df, window):
    high = df.rolling(window).max().iloc[-1].max()
    mean = df.rolling(window).mean()["OHLC_avg"].iloc[-1]
    low = df.rolling(window).min().iloc[-1].min()
    range = high - low
    std = df.rolling(window).std()["OHLC_avg"].iloc[-1]

    return pd.DataFrame([high, mean, low, range, std])

day20 = get_summ(df, 20)
day60 = get_summ(df, 60)
day120 = get_summ(df, 120)
day250 = get_summ(df, 250)
summ = pd.concat([day20, day60, day120, day250], axis=1, ignore_index=True)
summ.columns = ["20 거래일(1달)", "60 거래일(분기)", "120 거래일(반기)", "250 거래일(연)"]
summ.index = ["고점", "평균", "저점", "레인지", "표준편차"]
# 요약표
st.dataframe(summ)


st.markdown("---")   # 구분 가로선


#요약그래프
x20 = df.tail(20)["OHLC_avg"]
x60 = df.tail(60)["OHLC_avg"]
x120 = df.tail(120)["OHLC_avg"]
x250 = df.tail(250)["OHLC_avg"]

fig_sum = go.Figure()
fig_sum.add_trace(go.Histogram(x=x250, name="1년", marker = list("red")))
fig_sum.add_trace(go.Histogram(x=x120, name="반기")
fig_sum.add_trace(go.Histogram(x=x60, name="분기"))
fig_sum.add_trace(go.Histogram(x=x20, name="1달"))

# Overlay both histograms
fig_sum.update_layout(barmode='overlay')
# Reduce opacity to see both histograms
fig_sum.update_traces(opacity=0.50, nbinsx=20)

st.subheader("기간별 비율 분포 ")
st.write("x축: 비율 / y축: 관측수")
st.plotly_chart(fig_sum)



    
    

st.markdown("---")   # 구분 가로선



st.subheader("일자별 가격비율 데이터")
st.write("OHLC_avg : 개별종목의 당일 시가, 고가, 저가, 종가 평균값의 비율")
st.dataframe(df[["Open", "Close", "OHLC_avg"]].sort_index(ascending=False))
