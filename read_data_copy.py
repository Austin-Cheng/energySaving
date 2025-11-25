import pandas as pd
from cfg import data_path, project_path
import os
from copy import deepcopy


def read_dynamic_data_1():
    return {
        "chiller_supply_temperature": {
            "max_step": 0.6,
            "up_limit": 12,
            "low_limit": 7
        },
        "cds_delta_temperature": {
            "max_step": None,
            "up_limit": 5,
            "low_limit": 0
        },
        "plr": {
            "max_step": None,
            "up_limit": 80,
            "low_limit": 10
        },
        "delta_press": {
            "max_step": 0.03,
            "up_limit": 1,
            "low_limit": 0
        },
        "cwp_num": {
            "max_step": 1,
            "up_limit": 5,
            "low_limit": 0
        }
    }


def read_dynamic_data():
    return {
        "chiller_supply_temperature": {
            "max_step": 0.6,
            "up_limit": 12,
            "low_limit": 7
        },
        "cds_delta_temperature": {
            "max_step": None,
            "up_limit": 5,
            "low_limit": 0
        },
        "plr": {
            "max_step": None,
            "up_limit": 100,
            "low_limit": 0
        },
        "delta_press": {
            "max_step": 0.03,
            "up_limit": 1,
            "low_limit": 0
        },
        "cwp_num": {
            "max_step": 1,
            "up_limit": 5,
            "low_limit": 0
        }
    }


def read_action_switch_data():
    return {
        'chr_12_num': 'on',
        'chr_3_num': 'on',
        'cdp_123_num': 'off',
        'cdp_45_num': 'off',
        'ct_123_num': 'off',
        'cwp_123_num': 'off',
        'cwp_45_num': 'off',
        'delta_press': 'off',
        'chiller_supply_temperature': 'off',
        'ct_out_temperature': 'off',
        'cls_delta_temperature': 'off',
    }


def read_history_point_data():
    return {}


def read_latest_point_data_1():
    base_data = {
        'chr_12_num': 0,
        'chr_3_num': 0,
        'cds_cooling': 0,
        'cds_cop': 0,
        'chr_1_fault': 0,
        'chr_2_fault': 0,
        'chr_3_fault': 0,
        'chr_1_mode': 1,
        'chr_2_mode': 1,
        'chr_3_mode': 1,
        'chr_1_state': 0,
        'chr_2_state': 0,
        'chr_3_state': 0,
        'cls_delta_temperature': 0,
        'cls_cooling': 0,
        'outdoor_wet_temperature': 0,
        'cls_cop': 0,
        'ct_out_temperature': 0,
        'cdp_123_num': 0,
        'cdp_45_num': 0,
        'mpp_cdp_water_fluid': 0,
        'ct_123_num': 0,
        'cwp_123_num': 0,
        'cwp_45_num': 0,
        'delta_press': 0,
        'chiller_supply_temperature': 0,
        'mean_plr': 0,
        'cds_delta_temperature': 0
    }

    data = pd.read_excel(os.path.join(data_path, 'data_process.xlsx'), index_col=0, header=0)
    data['time'] = data.index
    res = []
    for d in data.to_dict(orient='records'):
        base_data.update(d)
        # print(base_data)
        res.append(deepcopy(base_data))
    return res


def read_latest_point_data():
    base_data = {
        'chr_12_num': 0,
        'chr_3_num': 0,
        'cds_cooling': 0,
        'cds_cop': 0,
        'chr_1_fault': 0,
        'chr_2_fault': 0,
        'chr_3_fault': 0,
        'chr_1_mode': 1,
        'chr_2_mode': 1,
        'chr_3_mode': 1,
        'chr_1_state': 0,
        'chr_2_state': 0,
        'chr_3_state': 0,
        'cls_delta_temperature': 0,
        'cls_cooling': 0,
        'outdoor_wet_temperature': 0,
        'cls_cop': 0,
        'ct_out_temperature': 0,
        'cdp_123_num': 0,
        'cdp_45_num': 0,
        'mpp_cdp_water_fluid': 0,
        'ct_123_num': 0,
        'cwp_123_num': 0,
        'cwp_45_num': 0,
        'delta_press': 0,
        'chiller_supply_temperature': 0,
        'mean_plr': 0,
        'cds_delta_temperature': 0
    }

    data1 = pd.read_excel(os.path.join(data_path, 'test.xlsx'), index_col=0, header=0)
    data2 = pd.read_excel(os.path.join(data_path, 'test2.xlsx'), index_col=0, header=0)
    data3 = pd.read_excel(os.path.join(data_path, 'test3.xlsx'), index_col=0, header=0)
    data = pd.concat([data1, data2, data3], axis=1)
    data['time'] = data.index
    res = []
    for d in data.to_dict(orient='records'):
        base_data.update(d)
        # print(base_data)
        res.append(deepcopy(base_data))
    return res


def read_latest_point_data_save():
    return {
        'chr_12_num': 0,
        'chr_3_num': 0,
        'cds_cooling': 0,
        'cds_cop': 0,
        'chr_1_fault': 0,
        'chr_2_fault': 0,
        'chr_3_fault': 0,
        'chr_1_mode': 0,
        'chr_2_mode': 0,
        'chr_3_mode': 0,
        # 'chr_1_state': 1,
        # 'chr_2_state': 1,
        # 'chr_3_state': 1,
        # 'cls_delta_temperature': 2.0,
        # 'cls_cooling': 1000,
        # 'outdoor_wet_temperature': 28,
        # 'cls_cop': 4.0,
        # 'ct_out_temperature': 3.0,
        # 'cdp_123_num': 2,
        # 'cdp_45_num': 0,
        # 'mpp_cdp_water_fluid': 600,
        # 'ct_123_num': 3,
        # 'cwp_123_num': 2,
        # 'cwp_45_num': 0,
        # 'delta_press': 1.0,
        # 'chiller_supply_temperature': 10,
        # 'mean_plr': 70,
        # 'cds_delta_temperature': 2.0
    }


if __name__ == '__main__':
    read_latest_point_data()
