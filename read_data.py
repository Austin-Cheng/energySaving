import requests
import time

import pandas as pd
import mmap
import json
from utilities.utils import NumpyEncoder
from errors import BasicError
import os
from cfg import project_path, basic_cfg
import re


class RequestBackendAPI:
    def __init__(self):
        self.algorithm_key = os.path.basename(os.path.normpath(project_path))
        self.base_url = 'http://127.0.0.1:8080/internal/algorithm/{}'
        self.x_authorization = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlcyI6WyJURU5BTlRfQURNSU4iXSwidXNlcklkIjoiMjQ2MGJiOTAtNDhkYS00YmMyLWE0NWYtMzk2Mzk4YTMxNmIxIiwibG9naW5EZXZpY2VUeXBlIjoiUEMiLCJpc1B1YmxpYyI6ZmFsc2UsImxvZ2luSWQiOiI1YWU1ZGRmYy1hMWU5LTRhOGYtYTUzYy02OGQ1MDY0MDJlYzYiLCJuYW1lIjoi5LyB5Lia566h55CG5ZGYIiwicGhvbmUiOiIxODYwMDAwMDAwMSIsInRlbmFudElkIjoiMmYxMzgzMGEtNGRkZi0zZDc5LWI2ZDYtN2Q3OTE5MTU5NWE3IiwiaXNzIjoic3otbmltYnVzLmNvbSIsImlhdCI6MTczNTA5Njc4NiwiZXhwIjoxNzM1MTgzMTg2fQ.i6MQcdZarUvI5OvFLXeFB_hvdaJ2o4sgVf3Ixge428tg5nBcJ2-UTo-vkirDA8Llyn1HEADhq9ehZGGPkF653w'
        self.x_project = '5155ff71-853e-38d0-a7c6-e03ad5def510'

    @staticmethod
    def request_api(url, body, header=None, timeout=5, func_name=None):
        try:
            response = requests.post(url, json=body, headers=header, timeout=timeout)
        except requests.exceptions.Timeout:
            raise BasicError('500', '请求超时', f'dynamic-pai: 请求超时')
        response = json.loads(response.text)
        if response['er'] != -1:
            raise BasicError(response['er'], response['erMessage'], f'{func_name}:{response["items"]}')
        return response

    def read_dynamic_data(self):
        url = self.base_url.format('dynamicConfig')
        body = {
            'algorithmKey': self.algorithm_key
        }
        response = self.request_api(url, body, func_name='read_dynamic_data')
        response = {boundary['name']: boundary for boundary in response['items']}
        return response

    def read_action_switch_data(self):
        url = self.base_url.format('algorithmOutput')
        body = {
            'algorithmKey': self.algorithm_key
        }
        response = self.request_api(url, body, func_name='read_action_switch_data')
        return response['items']

    def read_history_point_data(self):
        url = self.base_url.format('batchInputQuery')
        body = {
            'timePeriods': basic_cfg['timePeriods'],
            'timeGranularity': basic_cfg['timeGranularity'],
            'algorithmKey': self.algorithm_key
        }
        response = self.request_api(url, body, timeout=60, func_name='read_history_point_data')
        line_size = response['items']['mmapInfo']['lineSize']
        columns = response['items']['fieldNames']

        # 打开文件
        with open(os.path.join(project_path, 'mmap/mmap'), 'r+b') as f:
            mmapped_file = mmap.mmap(f.fileno(), 0)
            df = pd.read_csv(mmapped_file, header=None, names=columns, parse_dates=['time'], nrows=line_size)

        df_filtered = df.dropna(subset=[col for col in df.columns if col != 'time'], how='all')
        return df_filtered.to_dict(orient='records')

    def read_latest_point_data(self):
        url = self.base_url.format('singleInputQuery')
        body = {
            'algorithmKey': self.algorithm_key,
            # 'time': '2024-07-05 01:30:00'
        }
        response = self.request_api(url, body, func_name='read_latest_point_data')
        return response['items']

    def write_action_data(self, data):
        data = {re.sub(r'Feedback$', 'Control', k): v for k, v in data.items()}
        url = self.base_url.format('inferenceResultSave')
        body = {
            'algorithmKey': self.algorithm_key,
            'batchId': data['batchId'],
            'inferenceTime': data['time'],
            'inferenceData': data
        }
        header = {
            'X-Authorization': self.x_authorization,
            'X-Project': self.x_project
        }
        body = json.dumps(body, cls=NumpyEncoder)
        self.request_api(url, body, header, 20, func_name='write_action_data')

    def write_state(self, state_obj):
        state_info = {
            'er': state_obj.status_code,
            'erMessage': state_obj.error_message,
            'items': state_obj.error_details
        }
        print(state_info)


requestor = RequestBackendAPI()


if __name__ == '__main__':
    # res = read_dynamic_data()
    # print(res)
    # res = read_action_switch_data()
    # print(res)
    # st = time.time()
    # res = requestor.read_latest_point_data()
    # for k, v in res.items():
    #     print(k, v)
    # print(res)
    # print(time.time() - st)
    pass
    # res = read_latest_point_data()
    # print(res)
    # outputs = {
    #     "time": "0000-00-00 00:00:00",
    #     "GcChillerNumber_12_ChillerNumbeControl":1,
    #     "GcChillerNumber_3_ChillerNumberControl":1,
    #     "GcCoolingWaterPumpNumber_123_CoolingWaterPumpNumberControl":1,
    #     "GcCoolingWaterPumpNumber_45_CoolingWaterPumpNumberControl":1,
    #     "MainCoolingWater_WaterDifferentialTemperatureControl":1,
    #     "GcCoolingTowerTempreture_CoolingTowerTempretureControl":1,
    #     "GcCoolingTowerNumber_CoolingTowerNumberControl":1,
    #     "GcChilledWaterPumpNumber_123_ChilledWaterPumpNumberControl":1,
    #     "GcChilledWaterPumpNumber_45_ChilledWaterPumpNumberControl":1,
    #     "MainChilledWater_WaterDifferentialPressureControl":1,
    #     "GcChillerTempreture_ChillerTempretureControl":1
    # }
    # write_action_data(outputs)
