import streamlit as st
import pandas as pd
import vectorbt as vbt
import FinanceDataReader as fdr
import plotly.graph_objects as go
pd.options.plotting.backend = "plotly"




st.title("삼성전자우/삼성전자 패어트레이딩 예시")

st.subheader("거래규칙 요약")

st.write('''
    - 삼성전자우/삼성전자의 시가와 종가를 나누어 가격비율을 구함
    - 시가를 기준으로 진입 및 청산신호 생성
    - 종가를 기준으로 진입 및 청산 실행
    ---
    [진입 및 청산 신호]
    1) 시가 가격비율의 룩백 기간의 롤링 평균과 표준편차를 구함
    2) 가격비율의 시가가 지정한 표준편차 상단을 상회하면 페어 매도(삼성전자우 매도, 삼성전자 매수) 종가 진입
    3) 가격비율의 시가가 지정한 표준편차 하단을 하회하면 페어 매수(삼성전자우 매수, 삼성전자 매도) 종가 진입
    4) 청산은 가격비율의 시가가 평균을 터치(매도시 하회, 매수시 상회)시 종가 청산 
    '''
    )

st.markdown("---")   # 구분 가로선

st.subheader("가격비율")

start_date = "2010-01-01"
삼성전자우 = fdr.DataReader('005935', start_date)
삼성전자 = fdr.DataReader('005930', start_date)

ratio = 삼성전자우 / 삼성전자
ratio = ratio[["Open", "High", "Low", "Close", "Volume"]]

fig_1 = ratio.vbt.ohlcv().plot()
st.plotly_chart(fig_1)


