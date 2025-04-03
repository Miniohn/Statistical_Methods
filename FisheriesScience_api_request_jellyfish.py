import requests
import pandas as pd
from datetime import datetime
from time import sleep

# 사용자 설정 
API_KEY = 'qPwOeIrU-2504-XTXNAU-1096'
SDATE = '20240101' # 1차 20220601 2차 20230101 3차 20240101
EDATE = '20240731' # 1차 20221231 2차 20231231 3차 20240630

# 1. 주간보고 목록에서 srcode 수집
list_url = f"https://www.nifs.go.kr/OpenAPI_json?id=jellyList&key={API_KEY}&sdate={SDATE}&edate={EDATE}"
res = requests.get(list_url)
data = res.json()

# srcode 직접 구성 (inpt_date + "00")
srcodes = [item['inpt_date'] + '00' for item in data['body']['item']]
print(f"[INFO] {len(srcodes)}개의 srcode를 수집했습니다.")

# 2. 지역별 출현율 컬럼 정의
target_columns = {
    "충남":   ("nom_ratio_03", "bor_ratio_03", "etc_ratio_03"),
    "전남(남해)": ("nom_ratio_06", "bor_ratio_06", "etc_ratio_06"),
    "경남":   ("nom_ratio_07", "bor_ratio_07", "etc_ratio_07"),
    "부산":   ("nom_ratio_08", "bor_ratio_08", "etc_ratio_08"),
    "울산":   ("nom_ratio_09", "bor_ratio_09", "etc_ratio_09"),
    "경북":   ("nom_ratio_10", "bor_ratio_10", "etc_ratio_10"),
    "강원도": ("nom_ratio_11", "bor_ratio_11", "etc_ratio_11"),
    "제주도": ("nom_ratio_12", "bor_ratio_12", "etc_ratio_12"),
}

# 3. 상세정보 요청 및 데이터 수집
results = []

for srcode in srcodes:
    try:
        detail_url = f"https://www.nifs.go.kr/OpenAPI_json?id=jellyDetail2&key={API_KEY}&srcode={srcode}"
        res = requests.get(detail_url)
        item = res.json().get('body', {}).get('item', [])
        if not item:
            continue
        item = item[0]

        # 조사일시 파싱
        rdate_raw = item.get('rdate', '').replace('.', '').replace('-', '')[:8]
        try:
            rdate_dt = datetime.strptime(rdate_raw, '%Y%m%d')
        except ValueError:
            continue

        if not (datetime(2024, 1, 1) <= rdate_dt <= datetime(2024, 7, 31)): 
            continue

        # 지역별 출현율 데이터 추출
        for region, (nom, bor, etc) in target_columns.items():
            results.append({
                "조사일": rdate_dt.strftime('%Y-%m-%d'),
                "지역": region,
                "노무라입깃해파리 출현율": item.get(nom, ''),
                "보름달물해파리 출현율": item.get(bor, ''),
                "기타 해파리 출현율": item.get(etc, '')
            })

        sleep(0.1)  # 과도한 요청 방지
    except Exception as e:
        print(f"[ERROR] srcode {srcode} 처리 중 오류 발생: {e}")
        continue

# 4. 결과 저장
df = pd.DataFrame(results)

df

df.to_csv("/Users/haley/Desktop/2025-1/S_method/need_preprocessing/region_jellyfish_2405.csv", 
          index=False, encoding='UTF-8')