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
    def get_latest_date_from_csv(filename, date_column):
        try:
            df = pd.read_csv(filename)
            latest_date = pd.to_datetime(df[date_column]).max()
            return (latest_date + timedelta(days=1)).strftime('%Y%m%d')  # 최신 날짜 + 1일
        except FileNotFoundError:
            # 파일이 없는 경우 기본 시작 날짜 반환
            return '19900101'

    # 동행지수순환변동치 데이터
    startdate_동행지수 = get_latest_date_from_csv('동행지수순환변동치.csv', 'datetime')[:6]  # YYYYMM까지만 추출
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
    df1[['datetime', 'DATA_VALUE']].to_csv('동행지수순환변동치.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
    df2[['datetime', 'DATA_VALUE']].to_csv('선행지수순환변동치.csv', index=False, mode='a', header=False, encoding='utf-8-sig')

    # KOSPI.csv 파일에서 마지막 날짜 가져오기
    def get_latest_date_from_kospi(filename):
        try:
            # 필요한 행부터 데이터 읽기 (첫 두 줄 스킵)
            df = pd.read_csv(filename)  # 첫 두 줄 스킵
            df.columns = df.columns.str.strip()  # 열 이름에 공백 제거
            
            # 'Date' 열의 마지막 값 가져오기
            last_date = df.iloc[-1, 0]  # 가장 마지막 행의 'Date' 열 값
            
            # 문자열 날짜를 datetime 객체로 변환 후 하루 더하기
            latest_date = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            
            return latest_date
        except FileNotFoundError:
            # 파일이 없으면 기본 시작 날짜 반환
            return '1990-01-01'
        except Exception as e:
            print(f"Error processing KOSPI.csv: {e}")
            return '1990-01-01'
        
    # KOSPI 데이터 가져오기 및 CSV 저장
    enddate_kospi = datetime.now().strftime('%Y-%m-%d')
    latest_kospi_date = get_latest_date_from_kospi('KOSPI.csv')
    print("latest_kospi_date : ", latest_kospi_date, "enddate_kospi :", enddate_kospi)
    
    try:
        # KOSPI 데이터 다운로드
        kospi = yf.download('^KS11', latest_kospi_date, enddate_kospi, auto_adjust=True)
        print(kospi)  # 다운로드한 데이터 출력

        # 데이터가 DataFrame 형식인지 확인
        if isinstance(kospi, pd.DataFrame):
            # 3번째 인덱스 이후의 데이터 필터링
            kospi_cleaned = kospi.iloc[3:]  # iloc을 사용해 행을 선택
            print(kospi_cleaned)
        else:
            print("kospi 데이터가 올바른 DataFrame 형식이 아닙니다.")
        
        # 기존 CSV 파일 읽기
        try:
            # 기존 CSV 파일이 존재하는지 확인 
            file_exists = os.path.exists('KOSPI.csv')
        
            # 기존 CSV 파일 읽기 및 새 데이터 추가
            with open('KOSPI.csv', mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)

                # 새 데이터 추가 (각 행을 바로 추가)
                for index, row in kospi_cleaned.iterrows():
                    # 인덱스를 날짜로 변환하고, 각 데이터만 추가
                    row_data = [row.name.strftime('%Y-%m-%d')] + list(row)  # 날짜 + 값들
                    writer.writerow(row_data)

            # CSV 파일 읽기
            df_kospi = pd.read_csv('KOSPI.csv')
            
            # 마지막 몇 줄 출력
            print(df_kospi.tail())  # 최근 데이터 확인

        except FileNotFoundError:
            # 파일이 없으면 헤더와 함께 저장
            kospi.to_csv('KOSPI.csv', mode='w', header=False, index=False, encoding='utf-8-sig')
    
    except Exception as e:
        print("Error downloading KOSPI data:", e)
    
    # USD/KRW 환율 데이터 가져오기 (한국은행 API에서 FXX001으로 가져오기)
    startdate_usdkrw = get_latest_date_from_csv('USD_KRW.csv', 'datetime')
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
    df_usd_krw[['datetime', 'DATA_VALUE']].to_csv('USD_KRW.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
except Exception as e:
    print(f"Error occurred: {e}")
    exit(1)  # 명시적으로 종료 코드 설정
