import json
import os
from cfg import cfg_path


point_map = json.load(open(os.path.join(cfg_path, 'point_mappings_save.json'), 'r', encoding='UTF-8'))


def dp_fluid(data):
    if data['point'][point_map['cls_delta_temperature']] != 0:
        fluid = data['point'][point_map['cls_cooling']] / data['point'][point_map['cls_delta_temperature']]
    else:
        fluid = None
    data['point'].update({'mpp_cdp_water_fluid': fluid})


def dp_mean_plr(data):
    chr_12_num = data['point'][point_map['chr_12_num']]
    chr_3_num = data['point'][point_map['chr_3_num']]
    chr_12_cap = data['rating']['chr_12_cap']
    chr_3_cap = data['rating']['chr_3_cap']
    load = data['point'][point_map['cds_cooling']]

    if chr_12_num or chr_3_num:
        data['point'][point_map['mean_plr']] = load / (chr_12_cap * chr_12_num + chr_3_cap * chr_3_num) * 100


def dp_chr_state(data):
    if data['switch'][point_map['chr_12_num']] == 'on':
        if data['point'][point_map['chr_12_num']] == 2:
            data['point'][point_map['chr_1_state']] = 1
            data['point'][point_map['chr_2_state']] = 1
        elif data['point'][point_map['chr_12_num']] == 1:
            data['point'][point_map['chr_1_state']] = 1
            data['point'][point_map['chr_2_state']] = 0
        else:
            data['point'][point_map['chr_1_state']] = 0
            data['point'][point_map['chr_2_state']] = 0

    if data['switch'][point_map['chr_3_num']] == 'on':
        if data['point'][point_map['chr_3_num']] == 1:
            data['point'][point_map['chr_3_state']] = 1
        else:
            data['point'][point_map['chr_3_state']] = 0
