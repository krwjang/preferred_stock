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
    1) 시가 가격비율의 룩백 기간의 평균과 표준편차를 구함
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

fig_1 = ratio[["Open", "Close"]].vbt.plot()
st.plotly_chart(fig_1)



st.markdown("---")   # 구분 가로선
st.subheader("신호생성 및 시뮬레이션 예시")
st.write('''
    - 파라메터 : 룩백 기간 50일, 표준편차 2배 
    - 1회 거래비용 : 0.5% (2종목 왕복거래)
    ''')

# 파라메터 ##############
window = 50
std = 2
########################

bband = vbt.BBANDS.run(ratio["Open"], window=window, alpha=std)

long_enter = bband.lower_above(ratio["Open"])
short_enter = bband.upper_below(ratio["Open"])
long_exit = bband.middle_crossed_below(ratio["Open"])
short_exit = bband.middle_crossed_above(ratio["Open"])

# 시그널은 시가기준, 거래수행은 종가기준으로 수행
pf = vbt.Portfolio.from_signals(
    close = ratio["Close"],   # 종가 기준 
    entries = long_enter,
    exits = long_exit,
    short_entries = short_enter,
    short_exits = short_exit,
    # 왕복 수수료 및 슬립피지 0.5%
    fees = 0.0025,
    # sl_stop = 0.10,  # 스탑로스
    freq = 'd'
)


fig_pf = pf.plot()
st.plotly_chart(fig_pf)

st.write('''
    거래결과 요약
    ''')
df = pd.DataFrame(pf.stats())
st.dataframe(df)

st.write('''
    드로우다운
    ''')
fig_dd = pf.plot(subplots=["drawdowns", "underwater"])
st.plotly_chart(fig_dd)




st.markdown("---")   # 구분 가로선
st.subheader("파라메터 테스트 결과 참고")
st.write('''
    이동평균 길이와 표준편차 배수에 따른 샤프지수
    ''')

def test_band(window=50, alpha=2):
    bband = vbt.BBANDS.run(ratio["Open"], window=window, alpha=alpha)
    
    long_enter = bband.lower_above(ratio["Open"])
    short_enter = bband.upper_below(ratio["Open"])
    long_exit = bband.middle_crossed_below(ratio["Open"])
    short_exit = bband.middle_crossed_above(ratio["Open"])
    
    # 시그널은 시가기준, 거래수행은 종가기준으로 수행
    pf = vbt.Portfolio.from_signals(
        close = ratio["Close"],   # 종가 기준 
        entries = long_enter,
        exits = long_exit,
        short_entries = short_enter,
        short_exits = short_exit,
        # fees = 0.0025,   # 왕복 수수료 및 슬립피지 0.5%
        fees = ((0.015 + 0.1) / 100) * 2,   # (뱅키스 0.015% + 슬리피지 0.1%) * 2종목 = 0.23%
        freq = 'd'
    )

    return pf.stats([
        'total_return', 
        'total_trades', 
        'win_rate', 
        'expectancy',
        'sharpe_ratio',
        'calmar_ratio',
        'sortino_ratio'  
    ])

from itertools import product

MA = range(10, 210, 10)
SD = [0.5, 1, 1.5, 2, 2.5, 3]
comb = list(product(MA, SD))

comb_stats = [
    test_band(window=MA, alpha=SD)
    for MA, SD in comb
]

comb_stats_df = pd.DataFrame(comb_stats)

comb_stats_df.index = pd.MultiIndex.from_tuples(
    comb, 
    names=['MA', 'SD'])

fig_3 = comb_stats_df['Sharpe Ratio'].vbt.heatmap()
st.plotly_chart(fig_3)


# st.write('''
#     이동평균(MA) 길이와 표준편차(SD) 배수에 따른 소티노지수 결과
#     ''') 
# fig_4 = comb_stats_df['Sortino Ratio'].vbt.heatmap().show()
# st.plotly_chart(fig_4)


         
         
st.markdown("---")   # 구분 가로선
st.subheader("수익률 상위 10개 파라메터 ")

st.dataframe(comb_stats_df.sort_values(by="Total Return [%]", ascending=False).head(10))

st.write('''
    본 테스트는 거래전략 구축을 위한 하나의 예시이며 과거 데이터에 오버피팅 가능성이 있어 미래 수익률을 보장하지 않습니다.
    ''')



