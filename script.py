import requests
import pandas as pd

# API Key와 URL 설정
apikey='JYPDDDCMTDNB0AOZLW0K'
# 발급일자 : 20241228, 만료일자 : 20261228
url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/1/100/901Y067/M/199001/202412'
response = requests.get(url)
result = response.json()

# 전체 데이터 가져오기
list_total_count = int(result['StatisticSearch']['list_total_count'])
list_count = int(list_total_count / 100) + 1

rows = []
for i in range(list_count):
    start = str(i * 100 + 1)
    end = str((i + 1) * 100)
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{apikey}/json/kr/{start}/{end}/901Y067/M/199001/202412'
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

# CSV 파일 저장
df1[['datetime', 'DATA_VALUE']].to_csv('동행지수순환변동치.csv', index=False, encoding='utf-8-sig')
df2[['datetime', 'DATA_VALUE']].to_csv('선행지수순환변동치.csv', index=False, encoding='utf-8-sig')
