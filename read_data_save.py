import requests
from cfg import ALGORITHM_KEY
import time

import pandas as pd
import mmap
import json


body = {
    'algorithmKey': ALGORITHM_KEY
}


def read_dynamic_data():
    url = 'http://127.0.0.1:8080/internal/algorithm/dynamicConfig'
    response = requests.post(url, json=body)
    return response.text


def read_action_switch_data():
    url = 'http://127.0.0.1:8080/internal/algorithm/algorithmOutput'
    response = requests.post(url, json=body)
    return response.text


def read_history_point_data():
    url = 'http://127.0.0.1:8080/internal/algorithm/batchInputQuery'
    body_new = {
        'timePeriods': [
            {
                'startTime': '2024-09-01 00:00:00',
                'endTime': '2024-09-10 23:00:00'
            },
            {
                'startTime': '2024-07-01 00:00:00',
                'endTime': '2024-08-15 23:00:00'
            }
        ],
        'timeGranularity': 'MINUTES_5',
        'algorithmKey': ALGORITHM_KEY
    }

    response = requests.post(url, json=body_new, timeout=60)
    info = json.loads(response.text)
    line_size = info['items']['mmapInfo']['lineSize']
    columns = info['items']['fieldNames']
    print(line_size)

    # 打开文件
    with open('/opt/data/python/energy-saving/mmap/mmap', 'r+b') as f:
        mmapped_file = mmap.mmap(f.fileno(), 0)
        df = pd.read_csv(mmapped_file, header=None, names=columns, parse_dates=['time']).head(line_size)

    df_filtered = df.dropna(subset=[col for col in df.columns if col != 'time'], how='all')
    return df_filtered.to_dict(orient='records')


def read_latest_point_data():
    url = 'http://127.0.0.1:8080/internal/algorithm/singleInputQuery'
    response = requests.post(url, json=body)
    return response.text


if __name__ == '__main__':
    # res = read_dynamic_data()
    # print(res)
    # res = read_action_switch_data()
    # print(res)
    st = time.time()
    res = read_latest_point_data()
    print(res)
    print(time.time() - st)
    pass
    # res = read_latest_point_data()
    # print(res)
