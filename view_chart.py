import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# 절대 경로로 chart.html 저장
output_dir = os.path.join(os.getcwd(), "chart_files")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 필요한 파일 목록
required_files = [
    "KOSPI.csv",
    "KOSPI_add.csv",
    "동행지수순환변동치.csv",
    "동행지수순환변동치_add.csv",
    "선행지수순환변동치.csv",
    "선행지수순환변동치_add.csv",
    "USD_KRW.csv",
    "USD_KRW_add.csv"
]

# 파일 존재 여부를 확인하고, 없으면 대기
while True:
    missing_files = [file for file in required_files if not os.path.exists(file)]
    if not missing_files:
        print("모든 파일이 존재합니다.")
        break
    else:
        print(f"다음 파일이 존재하지 않습니다: {missing_files}")
        print("5초 후 다시 확인합니다...")
        time.sleep(5)
        
try:
    # 작업 디렉토리 확인
    print("현재 작업 디렉토리:", os.getcwd())

    # KOSPI 데이터 결합
    kospi_df = pd.read_csv('KOSPI.csv', skiprows=3)
    print(kospi_df)
    kospi_add_df = pd.read_csv('KOSPI_add.csv', skiprows=3)
    print(kospi_add_df)
    kospi_df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    kospi_add_df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    kospi_df['datetime'] = pd.to_datetime(kospi_df['Date'])
    kospi_add_df['datetime'] = pd.to_datetime(kospi_add_df['Date'])
    kospi_combined = pd.concat([kospi_df[['datetime', 'Close']], kospi_add_df[['datetime', 'Close']]], ignore_index=True)
    kospi_combined = kospi_combined.drop_duplicates(subset='datetime', keep='last')  # 중복 제거

    print(kospi_combined)
    
    # 최신 날짜(last_date) 추출
    last_date = kospi_combined['datetime'].max().strftime('%Y-%m-%d')

    # 동행지수 순환변동치 결합
    df1 = pd.read_csv('동행지수순환변동치.csv')
    df1_add = pd.read_csv('동행지수순환변동치_add.csv')
    df1.columns = ['datetime', 'DATA_VALUE']
    df1_add.columns = ['datetime', 'DATA_VALUE']
    df1['datetime'] = pd.to_datetime(df1['datetime'])
    df1_add['datetime'] = pd.to_datetime(df1_add['datetime'])
    df1_combined = pd.concat([df1, df1_add], ignore_index=True)
    df1_combined = df1_combined.drop_duplicates(subset='datetime', keep='last')  # 중복 제거

    # 선행지수 순환변동치 결합
    df2 = pd.read_csv('선행지수순환변동치.csv')
    df2_add = pd.read_csv('선행지수순환변동치_add.csv')
    df2.columns = ['datetime', 'DATA_VALUE']
    df2_add.columns = ['datetime', 'DATA_VALUE']
    df2['datetime'] = pd.to_datetime(df2['datetime'])
    df2_add['datetime'] = pd.to_datetime(df2_add['datetime'])
    df2_combined = pd.concat([df2, df2_add], ignore_index=True)
    df2_combined = df2_combined.drop_duplicates(subset='datetime', keep='last')  # 중복 제거

    # USD/KRW 환율 결합
    df_usd_krw = pd.read_csv('USD_KRW.csv')
    df_usd_krw_add = pd.read_csv('USD_KRW_add.csv')
    df_usd_krw.columns = ['datetime', 'DATA_VALUE']
    df_usd_krw_add.columns = ['datetime', 'DATA_VALUE']
    df_usd_krw['datetime'] = pd.to_datetime(df_usd_krw['datetime'])
    df_usd_krw_add['datetime'] = pd.to_datetime(df_usd_krw_add['datetime'])
    df_usd_krw_combined = pd.concat([df_usd_krw, df_usd_krw_add], ignore_index=True)
    df_usd_krw_combined = df_usd_krw_combined.drop_duplicates(subset='datetime', keep='last')  # 중복 제거

    print(df_usd_krw_combined)
    
    # 그래프 그리기
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],  # 두 번째 y축 추가
    )
    
    # 동행지수 순환변동치
    fig.add_trace(
        go.Scatter(x=df1_combined['datetime'], y=df1_combined['DATA_VALUE'], name="동행지수순환변동치"),
        secondary_y=False,
    )
    
    # 선행지수 순환변동치
    fig.add_trace(
        go.Scatter(x=df2_combined['datetime'], y=df2_combined['DATA_VALUE'], name="선행지수순환변동치"),
        secondary_y=False,
    )
    
    # KOSPI 데이터
    fig.add_trace(
        go.Scatter(x=kospi_combined['datetime'], y=kospi_combined['Close'], name="KOSPI"),
        secondary_y=True,
    )
    
    # USD/KRW 환율 데이터
    fig.add_trace(
        go.Scatter(x=df_usd_krw_combined['datetime'], y=df_usd_krw_combined['DATA_VALUE'], name="USD/KRW"),
        secondary_y=True,
    )
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_text=f'선행지수변동치와 동행지수순환변동치, KOSPI, USD/KRW ({last_date})',
        title={'x': 0.5, 'y': 0.9},  # 중앙 정렬
        xaxis=dict(
            title='날짜',
            tickformat="%y-%m-%d",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikedash="solid",
        ),
        yaxis=dict(
            title='동행지수',
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikecolor="blue",
            spikethickness=2,
        ),
        yaxis2=dict(
            title='KOSPI 및 USD/KRW',
            overlaying='y',
            side='right',
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikecolor="red",
            spikethickness=2,
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        dragmode="zoom",
        spikedistance=-1,
    )
    
    # HTML 파일로 저장
    fig.write_html(os.path.join(output_dir, "chart.html"))
    
    if os.path.exists("chart_files/chart.html"):
        print("chart.html 파일이 정상적으로 생성되었습니다.")
        print("HTML 파일이 생성되었습니다. 'chart.html' 파일을 열어보세요.")
    else:
        print("chart.html 파일 생성에 실패했습니다.")
    
except Exception as e:
    print(f"Error occurred: {e}")
