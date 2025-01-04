import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 절대 경로로 chart.html 저장
output_dir = os.path.join(os.getcwd(), "chart_files")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
try:
    # 작업 디렉토리 확인
    print("현재 작업 디렉토리:", os.getcwd())

    # CSV 파일 읽기
    df1 = pd.read_csv('동행지수순환변동치.csv', parse_dates=['datetime'])
    df2 = pd.read_csv('선행지수순환변동치.csv', parse_dates=['datetime'])
    df_usd_krw = pd.read_csv('USD_KRW.csv', parse_dates=['datetime'])
    
    # KOSPI 데이터 CSV 파일 읽기
    kospi = pd.read_csv('KOSPI.csv', skiprows=3)  # 첫 세 줄을 건너뛰고 데이터 읽기
    
    # 열 이름 설정
    kospi.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    
    # 'Date' 열을 datetime 형식으로 변환
    kospi['datetime'] = pd.to_datetime(kospi['Date'])
    
    # CSV 파일 내용 확인
    print("동행지수순환변동치.csv 내용:")
    print(df1.head())
    
    print("선행지수순환변동치.csv 내용:")
    print(df2.head())
    
    print("USD/KRW.csv 내용:")
    print(df_usd_krw.head())
    
    print("KOSPI.csv 내용:")
    print(kospi.head())
    
    # 그래프 그리기
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],  # 두 번째 y축 추가
    )
    
    # 동행지수 순환변동치
    fig.add_trace(
        go.Scatter(x=df1['datetime'], y=df1['DATA_VALUE'], name="동행지수순환변동치"),
        secondary_y=False,
    )
    
    # 선행지수 순환변동치
    fig.add_trace(
        go.Scatter(x=df2['datetime'], y=df2['DATA_VALUE'], name="선행지수순환변동치"),
        secondary_y=False,
    )
    
    # KOSPI 데이터
    fig.add_trace(
        go.Scatter(x=kospi['datetime'], y=kospi['Close'], name="KOSPI"),
        secondary_y=True,
    )
    
    # USD/KRW 환율 데이터
    fig.add_trace(
        go.Scatter(x=df_usd_krw['datetime'], y=df_usd_krw['DATA_VALUE'], name="USD/KRW"),
        secondary_y=True,
    )
    
    # 레이아웃 업데이트
    fig.update_layout(
        title_text='선행지수변동치와 동행지수변동치, KOSPI, USD/KRW',
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
    # 차트를 그려서 chart_files 폴더에 저장
    fig.write_html(os.path.join(output_dir, "chart.html"))
    
    if os.path.exists("chart_files/chart.html"):
        print("chart.html 파일이 정상적으로 생성되었습니다.")
        print("HTML 파일이 생성되었습니다. 'chart.html' 파일을 열어보세요.")
    else:
        print("chart.html 파일 생성에 실패했습니다.")
    
except Exception as e:
    print(f"Error occurred: {e}")

