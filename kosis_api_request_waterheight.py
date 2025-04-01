### "And the patriarchs, moved with envy, sold Joseph into Egypt: but God was with him"

# KOSIS API request_wave height

# import packages
import requests
import pandas as pd
from datetime import datetime, timedelta
import time


# option
API_URL = "http://apis.data.go.kr/1360000/BeachInfoservice/getWhBuoyBeach"
API_KEY = "MY_API"
beach_nums = [231, 313, 308, 345, 198, 250, 70, 273, 186, 329, 347, 305]
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 6, 30)
time_str = "1500"  # 3pm

results = []

# loop for date
current_date = start_date

while current_date <= end_date:
    search_time = current_date.strftime("%Y%m%d") + time_str

    for beach_num in beach_nums:
        params = {
            "serviceKey": API_KEY,
            "beach_num": beach_num,
            "searchTime": search_time,
            "dataType": "JSON",
            "numOfRows": "10",
            "pageNo": "1"
        }

        try:
            response = requests.get(API_URL, params=params)
            data = response.json()

            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not isinstance(items, list):
                items = [items]

            for item in items:
                results.append({
                    "beach_num": item.get("beachNum"),
                    "date": item.get("tm"),
                    "wave_height": item.get("wh")
                })

        except Exception as e:
            print(f"Error on {search_time} beach {beach_num}: {e}")

        time.sleep(0.2)  # 1sec - 5

    current_date += timedelta(days=1)

# change to DataFrame
df = pd.DataFrame(results)

df.head(30)

# save to csv
df.to_csv("/Users/haley/Desktop/2025-1/S_method/need_preprocessing/wave_height_2401_06.csv", 
          index=False)