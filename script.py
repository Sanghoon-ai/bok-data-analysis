import csv, os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

try:
    # API Key와 URL 설정
    apikey = 'JYPDDDCMTDNB0AOZLW0K'
    enddate = datetime.now().strftime('%Y%m%d')

    def safe_get_json(response, url=""):
        try:
            return response.json()
        except ValueError:
            print(f"❌ JSON 디코딩 실패! URL: {url}")
            print("응답 내용 일부:", response.text[:300])
            exit(1)

    def get_latest_date_from_csv(filename):
        try:
            df = pd.read_csv(filename, header=None, index_col=0, parse_dates=True)
            latest_date = df.index.max()
            if pd.notnull(latest_date):
                return (latest_date + timedelta(days=1)).strftime('%Y%m%d')
            else:
                return '19900101'
        except FileNotFoundError:
            return '19900101'
        except Exception as e:
            print(f"Error occurred while reading {filename}: {e}")
            return '19900101'

    startdate_동행지수 = get_latest_date_from_csv('동행지수순환변동치.csv')[:6]
    enddate_동행지수 = enddate[:6]

    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/1/100/901Y067/M/{startdate_동행지수}/{enddate_동행지수}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ 요청 실패! URL: {url}")
        print(f"상태 코드: {response.status_code}, 응답: {response.text[:300]}")
        exit(1)

    result = safe_get_json(response, url)
    list_total_count = int(result['StatisticSearch']['list_total_count'])
    list_count = int(list_total_count / 100) + 1

    rows = []
    for i in range(list_count):
        start = str(i * 100 + 1)
        end = str((i + 1) * 100)
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/{start}/{end}/901Y067/M/{startdate_동행지수}/{enddate_동행지수}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ 요청 실패! URL: {url}")
            print(f"상태 코드: {response.status_code}, 응답: {response.text[:300]}")
            exit(1)
        result = safe_get_json(response, url)
        rows.extend(result['StatisticSearch']['row'])

    df = pd.DataFrame(rows)
    df['datetime'] = pd.to_datetime(df['TIME'].str[:4] + '-' + df['TIME'].str[4:6] + '-01')
    df = df.astype({'DATA_VALUE': 'float'})
    df1 = df.loc[df['ITEM_NAME1'] == '동행지수순환변동치']
    df2 = df.loc[df['ITEM_NAME1'] == '선행지수순환변동치']
    print(df1)
    print(df2)
    df1[['datetime', 'DATA_VALUE']].to_csv('동행지수순환변동치_add.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
    df2[['datetime', 'DATA_VALUE']].to_csv('선행지수순환변동치_add.csv', index=False, mode='a', header=False, encoding='utf-8-sig')

    def get_latest_date_from_kospi_csv(filename):
        try:
            df = pd.read_csv(filename, header=2, index_col=0, parse_dates=True)
            latest_date = df.index.max()
            if pd.notnull(latest_date):
                return latest_date + timedelta(days=1)
            else:
                return pd.to_datetime('1996-01-01')
        except FileNotFoundError:
            return pd.to_datetime('1996-01-01')

    enddate_kospi = pd.to_datetime('today')
    startdate_kospi = get_latest_date_from_kospi_csv('KOSPI.csv')
    print("startdate_kospi:", startdate_kospi.strftime('%Y-%m-%d'), "enddate_kospi:", enddate_kospi.strftime('%Y-%m-%d'))

    try:
        kospi = yf.download('^KS11', start=startdate_kospi.strftime('%Y-%m-%d'), end=enddate_kospi.strftime('%Y-%m-%d'), auto_adjust=True)
        print(kospi)
        if not kospi.empty:
            kospi.to_csv('KOSPI_add.csv', mode='w', header=True, index=True, encoding='utf-8-sig')
            print("KOSPI 데이터를 KOSPI_add.csv에 저장했습니다.")
        else:
            print("KOSPI 데이터가 비어 있습니다.")
    except Exception as e:
        print(f"Error downloading KOSPI data: {e}")
        exit(1)

    # USD/KRW
    startdate_usdkrw = get_latest_date_from_csv('USD_KRW.csv')
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/1/100/731Y001/D/{startdate_usdkrw}/{enddate}/0000001'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ 환율 요청 실패! URL: {url}")
        print(f"상태 코드: {response.status_code}, 응답: {response.text[:300]}")
        exit(1)
    result = safe_get_json(response, url)

    rows_usd_krw = []
    if 'StatisticSearch' in result:
        list_total_count_usd = int(result['StatisticSearch']['list_total_count'])
        list_count_usd = int(list_total_count_usd / 100) + 1

        for i in range(list_count_usd):
            start = str(i * 100 + 1)
            end = str((i + 1) * 100)
            url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/{start}/{end}/731Y001/D/{startdate_usdkrw}/{enddate}/0000001'
            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ 환율 반복 요청 실패! URL: {url}")
                print(f"상태 코드: {response.status_code}, 응답: {response.text[:300]}")
                exit(1)
            result = safe_get_json(response, url)
            if 'StatisticSearch' in result:
                rows_usd_krw += result['StatisticSearch']['row']
            else:
                print("응답에서 'StatisticSearch' 없음.")
                exit(1)
    else:
        print("최초 환율 응답에 'StatisticSearch' 없음.")
        exit(1)

    df_usd_krw = pd.DataFrame(rows_usd_krw)
    df_usd_krw['datetime'] = pd.to_datetime(df_usd_krw['TIME'].str[:4] + '-' + df_usd_krw['TIME'].str[4:6] + '-01')
    df_usd_krw = df_usd_krw.astype({'DATA_VALUE': 'float'})
    print(df_usd_krw[['datetime', 'DATA_VALUE']])
    df_usd_krw[['datetime', 'DATA_VALUE']].to_csv('USD_KRW_add.csv', index=False, mode='a', header=False, encoding='utf-8-sig')

except Exception as e:
    print(f"🔥 최상위 예외 발생: {e}")
    exit(1)
