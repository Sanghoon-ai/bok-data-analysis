import csv, os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

try:
    # API Key와 URL 설정
    apikey='JYPDDDCMTDNB0AOZLW0K'
    # 발급일자 : 20241228, 만료일자 : 20261228
    
    # 오늘 날짜 가져오기
    enddate = datetime.now().strftime('%Y%m%d')

    # CSV 파일에서 최신 날짜 가져오기 함수
    def get_latest_date_from_csv(filename):
        try:
            # CSV 파일 읽기 (첫 열을 날짜로 사용)
            df = pd.read_csv(filename, header=None, index_col=0, parse_dates=True)
            print("csv 파일 df :", df)
            # 인덱스에서 가장 최근 날짜 가져오기
            latest_date = df.index.max()
    
            if pd.notnull(latest_date):
                # 날짜가 datetime 객체로 반환되므로 이를 올바르게 처리
                return (latest_date + timedelta(days=1)).strftime('%Y%m%d')
            else:
                # 날짜 값이 없을 경우 기본값 반환
                return '19900101'
        
        except FileNotFoundError:
            # 파일이 없으면 기본 시작 날짜 반환
            return '19900101'
    
        except Exception as e:
            # 다른 예외가 발생하면 오류 메시지 출력 후 기본 날짜 반환
            print(f"Error occurred while reading {filename}: {e}")
            return '19900101'

    # 동행지수순환변동치 데이터
    startdate_동행지수 = get_latest_date_from_csv('동행지수순환변동치.csv')[:6]  # YYYYMM까지만 추출
    enddate_동행지수 = enddate[:6]
    
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/1/100/901Y067/M/{startdate_동행지수}/{enddate_동행지수}'
    response = requests.get(url)
    result = response.json()
    
    # 전체 데이터 가져오기
    list_total_count = int(result['StatisticSearch']['list_total_count'])
    list_count = int(list_total_count / 100) + 1
    
    rows = []
    for i in range(list_count):
        start = str(i * 100 + 1)
        end = str((i + 1) * 100)
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/{start}/{end}/901Y067/M/{startdate_동행지수}/{enddate_동행지수}'
        response = requests.get(url)
        result = response.json()
        rows.extend(result['StatisticSearch']['row'])
    
    # 데이터프레임 생성
    df = pd.DataFrame(rows)
    
    # 데이터 전처리
    df['datetime'] = pd.to_datetime(df['TIME'].str[:4] + '-' + df['TIME'].str[4:6] + '-01')
    df = df.astype({'DATA_VALUE': 'float'})
    
    # 데이터 분리
    df1 = df.loc[df['ITEM_NAME1'] == '동행지수순환변동치']
    df2 = df.loc[df['ITEM_NAME1'] == '선행지수순환변동치']

    print(df1)
    print(df2)
    
    # CSV 파일 저장
    df1[['datetime', 'DATA_VALUE']].to_csv('동행지수순환변동치_add.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
    df2[['datetime', 'DATA_VALUE']].to_csv('선행지수순환변동치_add.csv', index=False, mode='a', header=False, encoding='utf-8-sig')

    # CSV 파일에서 가장 최근 날짜 가져오기 함수
    def get_latest_date_from_kospi_csv(filename):
        try:
            # CSV 파일 읽기 (첫 열이 날짜 값으로 사용됨)
            df = pd.read_csv(filename, header=None, index_col=0, parse_dates=True)
            latest_date = df.index.max()  # 인덱스에서 가장 최근 날짜 가져오기
            if pd.notnull(latest_date):
                # 날짜 + 1일 반환 (datetime 객체)
                return latest_date + timedelta(days=1)
            else:
                # 날짜 값이 없을 경우 기본값 반환
                return pd.to_datetime('1996-01-01')
        except FileNotFoundError:
            # 파일이 없으면 기본 시작 날짜 반환
            return pd.to_datetime('1996-01-01')

    # 날짜 설정 (datetime 객체로 설정)
    enddate_kospi = pd.to_datetime('today')  # 오늘 날짜
    # KOSPI 시작 날짜 설정
    startdate_kospi = get_latest_date_from_kospi_csv('KOSPI.csv')
    print("startdate_kospi :",startdate_kospi.strftime('%Y-%m-%d'))
    
    try:
        # KOSPI 데이터 다운로드
        kospi = yf.download('^KS11', start=startdate_kospi.strftime('%Y-%m-%d'), end=enddate_kospi, auto_adjust=True)
        print(kospi)  # 다운로드한 데이터 출력
    
        # 데이터가 비어있지 않다면
        if not kospi.empty:
            # CSV 파일로 저장 (헤더 포함, 인덱스 제외)
            kospi.to_csv('KOSPI_add.csv', mode='w', header=True, index=True, encoding='utf-8-sig')
            print("KOSPI 데이터를 KOSPI_add.csv에 저장했습니다.")
        else:
            print("KOSPI 데이터가 비어 있습니다. 날짜 범위를 확인해주세요.")
    
    except Exception as e:
        print(f"Error downloading KOSPI data: {e}")
    
    # USD/KRW 환율 데이터 가져오기 (한국은행 API에서 FXX001으로 가져오기)
    startdate_usdkrw = get_latest_date_from_csv('USD_KRW.csv')
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/1/100/731Y001/D/{startdate_usdkrw}/{enddate}/0000001'
    response = requests.get(url)
    result = response.json()
    
    rows_usd_krw = []
    if 'StatisticSearch' in result:
        list_total_count_usd = int(result['StatisticSearch']['list_total_count'])
        list_count_usd = int(list_total_count_usd / 100) + 1
    
        for i in range(list_count_usd):
            start = str(i * 100 + 1)
            end = str((i + 1) * 100)
            
            url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/{start}/{end}/731Y001/D/{startdate_usdkrw}/{enddate}/0000001'
            response = requests.get(url)
            result = response.json()
    
            if 'StatisticSearch' in result:
                rows_usd_krw += result['StatisticSearch']['row']
            else:
                print("응답에서 'StatisticSearch'가 없어서 데이터를 추가하지 못했습니다.")
    
    # 원/달러 환율 데이터 포맷팅
    df_usd_krw = pd.DataFrame(rows_usd_krw)
    df_usd_krw['datetime'] = pd.to_datetime(df_usd_krw['TIME'].str[:4] + '-' + df_usd_krw['TIME'].str[4:6] + '-01')
    df_usd_krw = df_usd_krw.astype({'DATA_VALUE': 'float'})
    print(df_usd_krw[['datetime', 'DATA_VALUE']])
    # 환율 데이터를 CSV로 저장
    df_usd_krw[['datetime', 'DATA_VALUE']].to_csv('USD_KRW_add.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
except Exception as e:
    print(f"Error occurred: {e}")
    exit(1)  # 명시적으로 종료 코드 설정
