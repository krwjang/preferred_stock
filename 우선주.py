import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr
pd.options.plotting.backend = "plotly"
import plotly.graph_objects as go


# 기초변수 설정
n_days = 100
now = datetime.now().date() + timedelta(days=1)
ago = now - timedelta(days=365)

ticker_pref = "005935"
ticker_comm = "005930"




# @st.cache_data
def read_price(preferred, common, start, end):
    '''
    우선주티커, 본주티커, 불러오기 시작일자
    '''
    preferred = fdr.DataReader(preferred, start=start, end=end)[['Open', 'High', 'Low', 'Close']]
    common = fdr.DataReader(common, start=start, end=end)[['Open', 'High', 'Low', 'Close']]
    ratio = preferred / common
    ratio["OHLCV_avg"] = (ratio.Open + ratio.High + ratio.Low + ratio.Close) / 4

    return ratio

df = read_price(ticker_pref, ticker_comm, start=ago, end=now)



st.title("삼성전자우/삼성전자 페어")


st.markdown("---")   # 구분 가로선


st.subheader("삼성전자우/삼성전자 가격비율 추이")
st.write("개별종목의 시고저종 시점의 비율임 (비율의 시고저종 아님)")
st.write("마우스 드래그 : 확대 / 더블클릭 : 축소")

fig = go.Figure(data=[go.Candlestick(
    increasing_line_color= 'red', decreasing_line_color= 'blue',
    x=df.index,
    open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close']
)])
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig)



# 전광판

preferred
common

col1, col2, col3 = st.columns(3)

last_sp_1m = mid["1M"].iloc[-1]
last_sp_2m = mid["2M"].iloc[-1]
last_sp_3m = mid["3M"].iloc[-1]
last_sp_6m = mid["6M"].iloc[-1]
last_sp_1y = mid["1Y"].iloc[-1]


col1.metric("1개월물", f"{last_sp_1m}원", round(mid["1M"].iloc[-1] - mid["1M"].iloc[-2], ndigits=3))
col2.metric("2개월물", f"{last_sp_2m}원", round(mid["2M"].iloc[-1] - mid["2M"].iloc[-2], ndigits=3))
col3.metric("3개월물", f"{last_sp_3m}원", round(mid["3M"].iloc[-1] - mid["3M"].iloc[-2], ndigits=3))
col4.metric("6개월물", f"{last_sp_6m}원", round(mid["6M"].iloc[-1] - mid["6M"].iloc[-2], ndigits=3))
col5.metric("1년물", f"{last_sp_1y}원", round(mid["1Y"].iloc[-1] - mid["1Y"].iloc[-2], ndigits=3))



st.markdown("---")   # 구분 가로선




st.subheader("기간별 가격비율 요약")

# 아래 고점 저점은 시고저종이 아니라 기간 관측값에서 고점저점임  <-- 매우중요
def get_summ(df, window):
    high = df.rolling(window).max().iloc[-1].max()
    mean = df.rolling(window).mean()["OHLCV_avg"].iloc[-1]
    low = df.rolling(window).min().iloc[-1].min()
    range = high - low
    std = df.rolling(window).std()["OHLCV_avg"].iloc[-1]

    return pd.DataFrame([high, mean, low, range, std])

day20 = get_summ(df, 20)
day60 = get_summ(df, 60)
day120 = get_summ(df, 120)
day250 = get_summ(df, 250)
summ = pd.concat([day20, day60, day120, day250], axis=1, ignore_index=True)
summ.columns = ["20 거래일(1달)", "60 거래일(분기)", "120 거래일(반기)", "250 거래일(연)"]
summ.index = ["고점", "평균", "저점", "레인지", "표준편차"]

st.dataframe(summ)
    


st.markdown("---")   # 구분 가로선



st.subheader("삼성전자우/삼성전자 가격비율 데이터")
st.write("개별종목의 시고저종 시점의 비율임 (OHLCV_avg : 당일 시고저종 평균값)")
st.dataframe(df.sort_index(ascending=False))
