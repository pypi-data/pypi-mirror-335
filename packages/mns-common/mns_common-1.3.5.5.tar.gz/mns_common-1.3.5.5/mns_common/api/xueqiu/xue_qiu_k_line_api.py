import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from loguru import logger
import requests
import pandas as pd


# year 年
#  quarter 季度
# month 月度
# week 周
# day 日
def get_xue_qiu_k_line(symbol, period):
    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"

    params = {
        "symbol": symbol,
        "begin": "1742574377493",
        "period": period,
        "type": "before",
        "count": "-120084",
        "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://xueqiu.com",
        "priority": "u=1, i",
        "referer": "https://xueqiu.com/S/SZ300879?md5__1038=n4%2BxgDniDQeWqxYwq0y%2BbDyG%2BYDtODuD7q%2BqRYID",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "cookie": "xq_a_token=cc9943aa6d41f0ae420f49b428f2f90a472b070a;"
                  " xqat=cc9943aa6d41f0ae420f49b428f2f90a472b070a; "
                  "xq_r_token=20869bd02083b2ef75d4d4b7654f827f00fdcd22;"
                  " xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTc0NDc2NTA3MCwiY3RtIjoxNzQyNDg4OD"
                  "kyNDc1LCJjaWQiOiJkOWQwbjRBWnVwIn0.Ep9IIWPMwb85xYIJ_pmYTDmUmcySD4t5nv4LpYSqdLJzNzqgvzGFx6vowXm-ZtyePuppJxd2YjJDREHu7OkvZk"
                  "qHRGMGQOhuCDzyMQjpND2yTgyOTNkn2hNs0e5p4FihaSeRmLu8vQDU17No3LjM3y4-0caZ-8LNJnOm0Wet1uOD7h9ASf7sLRQCjGyB-Pd4D2r-213umj7c6TD"
                  "V5ud3rfTsUlCG7DwWMAdIZGkew5CX2WRXOz-G2Duf3d4GMRggiaLHVsP6PSTzOGUQBF1zAg5hprkxK3J_dV1SdiuaAZxJDp3FCFQ5vG0JkcOs9CLB5z-92kQ2-"
                  "YEhAkd3PCpGKQ; cookiesu=251742488951389; u=251742488951389; is_overseas=0; Hm_lvt_1db88642e346389874251b5a1eded6e3=1742488952; "
                  "Hm_lpvt_1db88642e346389874251b5a1eded6e3=1742488952; HMACCOUNT=A216813C8A2D1B76; device_id=e7bd664c2ad4091241066c3a2ddbd736; "
                  "ssxmod_itna=eqIxgDB7q+0=ei7qqAKG7D8D9DQqqiIqGHDyxW9P0CGDLxn4GQDUiHxttBmPvc7EkqE5gD0yG3wDA5Dnzx7YDt=SpND0mTAc3qACQIwPw+Ocyrm2tfA"
                  "br4MWHlPP5jokUkpQw5xB3DExGkeeu77xiirx0rD0eDPxDYDGbWD7PDoxDrF8YDjl7pOUgwoz4DKx0kDY5Dw1RADiPD7ZBDkOcwXSvmFxDzFZLaqle42Di3N+EsEzRfDi5"
                  "x79cwD7v3DlaPFsdD0119FgoIiya2PpBEv40OD0ILF4BfuYoA8872wprrZQ4F2G0YjEDQ0DO03e7qSh5tY7t0sOGe2GDNQKc3xeY5ldw7xDipwGg2QIhxjhrCtccU5ZUB="
                  "+VcwwiGxCeBGPyew=jp=lDqQ4ZAqzBqPj0=jh1Fxq7De903iYLYD; ssxmod_itna2=eqIxgDB7q+0=ei7qqAKG7D8D9DQqqiIqGHDyxW9P0CGDLxn4GQDUiHxttBmPvc7E"
                  "kqE5wDDcA73imLDD7Djbb5NZaEoD/zpofwEa9m=Fn7T5jOiFKWsbAb9Qi=utFFLry0Ii9=+TINLqBPqzemrFP/ehSZRDixpiEh5WeA5WXGvaHoKw+rEINZbPjOApkpEQG8cm="
                  "rHCN=0DUoI+HxcF6Zohnh3hUEcTYQykDVyXyfHsX9eFZAlAHxdWq/5qZ=Eh0KCAV2xA2/yKFtivK+DzQb0sajPwql5xkzLh966v0g6MzzUlc4SFYAv3YKBjP7rhhOdqmKEa"
                  "j6C6PKp+Pq2QEP6heBX7BU7iG=GGLA6IrDjYvHCDh1tr93XpUr9X9rPjYUvWxPI0RBwHUpC+fs6xsg07+ifjd9gU26do2K0lLwRhhPfppAKj5+gow2IN3KLQ0K1P/mY9BKKYAt"
                  "2Qx/34rb5evohIrUI=DKe1djnDvrDnjwcBbgK2lzA3eQVix=46cxf77D9GKug6PLBL0Fi67Htrl2K5CP9PQDHb1Yjx0ttRKjCU7hE3GIs2Y88AdxfF+Iuc2=IenBfqW52ngad82Y"
                  "8KvKqn5xEiODXgYCKgGxyOjl4+v9bvIm120i2pN6o6dBRZqxpvsA4S9YP2TPjS+1/4ZnVeYQ+4=UCevs5P3Qf2x6w8s=U7dD=cvG1skhxiD8Kjl32RGPC=4FDHIrQQoKGnixsWzp"
                  "Fb7F=PlrD/3=0F6DNx2hDnr4RDW7WGYSiPQFihqY15iS7GAr44w1+x/3wnYQ4=rN/wOitjqZ0N0FRpxlw/7PGeZADD"
    }
    try:
        response = requests.get(
            url=url,
            params=params,
            headers=headers
        )

        if response.status_code == 200:
            response_data = response.json()
            df = pd.DataFrame(
                data=response_data['data']['item'],
                columns=response_data['data']['column']
            )
            # 处理DataFrame列（秒级时间戳）
            df['str_day'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()
            df["str_day"] = df["str_day"].dt.strftime("%Y-%m-%d")
            return df
        else:
            return pd.DataFrame()
    except BaseException as e:
        logger.error("同步股票年度数据出现异常:{},{}", symbol, e)


if __name__ == '__main__':
    test_df = get_xue_qiu_k_line('SZ000001', 'year')
    print(test_df)
