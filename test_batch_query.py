import requests
import pandas as pd


# 定义 API 的 URL
url = 'http://localhost:8080/internal/algorithm/batchInputQuery'
request_body = {
   'algorithmKey': "energy-saving-baiyue",
    'timeGranularity': 'MINUTES_5',
    'timePeriods': [{'startTime': '2024-07-05 00:00:00', 'endTime': '2024-07-08 00:00:00'}]
        }


# 发送 GET 请求
response = requests.post(url, json=request_body)
columns_to_print = ['GcChillerNumber_12_ChillerNumberFeedback','GcChillerNumber_3_ChillerNumberFeedback']

# 检查请求是否成功（状态码 200 表示成功）
if response.status_code == 200:
    # 解析响应内容为 JSON 格式
    data = response.json()
    print(data)

    fields = data['items']['fieldNames']
    file_path = data['items']['mmapInfo']['fileName']
    line_count = data['items']['mmapInfo']['lineSize']
    
    df = pd.read_csv(file_path, header=None, names=fields, nrows=line_count)
    df_top5 = df.head(100)
    print(df.loc[1:5, columns_to_print])
else:
    print(f"请求失败，状态码: {response.status_code}")
