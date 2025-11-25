import json
import os
from cfg import cfg_path


point_map = json.load(open(os.path.join(cfg_path, 'point_mappings_save.json'), 'r', encoding='UTF-8'))


class AFUColdSomeAction:
    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        cold_inds = []
        for i, arg_name in enumerate(data['agent']['action_args_name']):
            if data['switch'][arg_name] == 'off':
                cold_inds.append(i)

        for nominal_action in data['agent']['action_space']:
            for ind in cold_inds:
                if nominal_action[ind] != data['point']['action'][ind]:
                    if nominal_action in actions:
                        actions.remove(nominal_action)
                    print(f'remove action by AFUColdSomeAction: {nominal_action}')
        return actions


class AFUChrNumByDeviceFault:
    DESCRIPTION = """
        检查冷机是否出现故障，推荐结果应不包含故障冷机
    """
    INPUTS = [
        "chr_fault"
    ]
    INPUTS_DESCRIPTION = """
    chr_fault: 
        示例: (0, 1, 0)
        示例说明：(1#主机正常, 2#主机故障, 3#主机正常)
    """

    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        for nominal_action in data['agent']['action_space']:
            if (data['point'][point_map['chr_1_fault']] == 1 and data['point'][point_map['chr_2_fault']] == 1 and nominal_action[0] == 1) or (data['point'][point_map['chr_3_fault']] == 1 and nominal_action[1] == 1):
                actions.remove(nominal_action)
                print(f'remove action by AFUChrNumByDeviceFault: {nominal_action}')
        return actions


class AFUChrNumByLocalMode:
    DESCRIPTION = """
        检查主机是否允许AI控制。若存在某台主机不允许AI控制，需检查该主机当前的状态，在此状态的前提下，推荐其他主机是否开启。
    """
    INPUTS = [
        "chr_mode",
        "action"
    ]
    INPUTS_DESCRIPTION = """
    chr_mode:
        示例: (0, 1, 1)
        示例说明：(1#主机不允许, 2#主机允许, 3#主机允许)
    action:
        实时的action数据
    """

    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        for nominal_action in data['agent']['action_space']:
            if data['point'][point_map['chr_3_mode']] == 0 and nominal_action[1] != data['point']['action'][1]:
                actions.remove(nominal_action)
                print(f'remove action by AFUChrNumByLocalMode: {nominal_action}')
            if data['point'][point_map['chr_1_mode']] == 0 and data['point'][point_map['chr_2_mode']] == 0 and nominal_action[0] != int(data['point'][point_map['chr_1_state']] or data['point'][point_map['chr_2_state']]):
                actions.remove(nominal_action)
            if data['point'][point_map['chr_1_mode']] == 0 and data['point'][point_map['chr_1_state']] == 1 and nominal_action[0] != 1:
                actions.remove(nominal_action)
            if data['point'][point_map['chr_2_mode']] == 0 and data['point'][point_map['chr_2_state']] == 1 and nominal_action[0] != 1:
                actions.remove(nominal_action)

        return actions


class AFUChrNumByCoolingThreshold:
    DESCRIPTION = """
        冷机工作负载应不超过设置的主机冷量的上下限。
    """
    INPUTS = [
        "chr_cooling_threshold",
        "state"
    ]
    INPUTS_DESCRIPTION = """
    chr_mode: 
        示例: (0, 1, 1)
        示例说明：(1#主机不允许, 2#主机允许, 3#主机允许)
    cooling:
        实时的冷量数据
    """

    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        for nominal_action in data['agent']['action_space']:
            min_ = 1200 * data['boundary']['plr']['low_limit'] * nominal_action[0] / 100 + 2200 * data['boundary']['plr']['low_limit'] * nominal_action[1] / 100
            max_ = 1200 * data['boundary']['plr']['up_limit'] * nominal_action[0] / 100 + 2200 * data['boundary']['plr']['up_limit'] * nominal_action[1] / 100

            if data['point'][point_map['cds_cooling']] < min_ or data['point'][point_map['cds_cooling']] > max_:
                actions.remove(nominal_action)
                print(f'remove action by AFUChrNumByCoolingThreshold: {nominal_action}')
        return actions


class AFUCdpNumByChrNum:
    DESCRIPTION = """
        考虑冷却泵和主机的绑定关系。
    """
    INPUTS = [
        "chr_12_num",
        "chr_3_num"
    ]
    INPUTS_DESCRIPTION = """
    chr_state: 
        示例: (0, 1)
        示例说明：(1#主机和2#主机不开启, 3#主机开启)
    """

    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        if data['point'][point_map['chr_12_num']] is None or data['point'][point_map['chr_3_num']] is None:
            return set()

        if data['point'][point_map['chr_12_num']] == 0:
            for action in data['agent']['action_space']:
                if action[1] != 0:
                    if action in actions:
                        actions.remove(action)
        if data['point'][point_map['chr_3_num']] == 0:
            for action in data['agent']['action_space']:
                if action[0] != 0:
                    if action in actions:
                        actions.remove(action)
        return actions


class AFUChrSupplyTemp:
    DESCRIPTION = """
        调节幅度限制
        冷机负载率限制
        冷冻水供回水温差限制
    """
    INPUTS = [
        "supply_temp_sp",
        "plr",
        "delta_temp",
        "boundary"
    ]
    INPUTS_DESCRIPTION = """
    supply_temp_sp: 
        示例: (8.5)
        示例说明：(实际供水温度设置值)
    plr: 
        示例: (85)
        示例说明：(平均负载率)
    delta_temp: 
        示例: (3.5)
        示例说明：(冷冻水供回水温差)
    boundary: 
        示例: {'limit_supply_temp': {'max_step': 1.0}, 
                'plr': {'up_limit': 100, 'low_limit': 30}},
                'delta_temp': {'up_limit': 4.5, 'low_limit': 2.5}, 
                }
        示例说明：(约束条件)
    """

    @classmethod
    def filter(cls, data):
        potential_actions = []
        for action_tuple in data['agent']['action_space']:
            supply_temp = action_tuple[0]
            last_supply_temp = data['last_point'][point_map['chiller_supply_temperature']]
            plr_value = data['point'][point_map['mean_plr']]
            if abs(supply_temp - last_supply_temp) <= data['boundary']['chiller_supply_temperature']['max_step']:
                if ((plr_value <= data['boundary']['plr']['low_limit']+10) and (supply_temp < last_supply_temp)) or \
                        ((plr_value >= data['boundary']['plr']['up_limit']-10) and (supply_temp > last_supply_temp)) or \
                        ((plr_value > data['boundary']['plr']['low_limit']+10) and (plr_value < data['boundary']['plr']['up_limit']-10)):
                    if ((data['point'][point_map['cds_delta_temperature']] <= data['boundary']['cds_delta_temperature']['low_limit']) and (supply_temp >= last_supply_temp)) or \
                            ((data['point'][point_map['cds_delta_temperature']] >= data['boundary']['cds_delta_temperature']['up_limit']) and (supply_temp <= last_supply_temp)) or \
                            ((data['point'][point_map['cds_delta_temperature']] > data['boundary']['cds_delta_temperature']['low_limit']) and (
                                    data['point'][point_map['cds_delta_temperature']] < data['boundary']['cds_delta_temperature']['up_limit'])):
                        potential_actions.append(action_tuple)
        return set(potential_actions)


class AFUCWS:
    DESCRIPTION = """
        压差调节幅度限制
        冷机关联限制
    """
    INPUTS = [
        "action_space",
        "state_tuple",
        "boundary"
    ]
    INPUTS_DESCRIPTION = """
    action_space: 
        示例: (1, 1, 1.05)
        示例说明：(1#2#3#冷冻泵开启台数，4#5#冷冻泵开启台数，压差设置值)
    state_tuple: 
        示例: (850, 8.0, 1, 1)
        示例说明：(冷负荷， 冷冻水供水温度设定值，1#2#冷机开启台数， 3#冷机开启台数)
    boundary: 
        示例: {'pres_diff': {'max_step': 0.1}, 
                'cwp_num': {'min_num': 1}}
                }
        示例说明：(约束条件)
    """

    @classmethod
    def filter(cls, data):
        potential_actions = []
        for action_tuple in data['agent']['action_space']:
            cwp123_num, cwp45_num, pres_diff = action_tuple
            last_pres_diff = data['last_point'][point_map['delta_press']]
            if abs(pres_diff - last_pres_diff) <= data['boundary']['delta_press']['max_step']:
                if ((data['point']['state'][2] == 0 and data['point']['state'][3] == 0) and (cwp123_num + cwp45_num == data['boundary']['cwp_num']['low_limit'])) or \
                        ((data['point']['state'][2] == 0 and data['point']['state'][3] != 0) and (cwp123_num == 0 and cwp45_num > 0 and cwp45_num >= data['boundary']['cwp_num']['low_limit'])) or \
                        ((data['point']['state'][2] != 0 and data['point']['state'][3] == 0) and (cwp123_num > 0 and cwp123_num >= data['boundary']['cwp_num']['low_limit'] and cwp45_num == 0)) or \
                        ((data['point']['state'][2] != 0 and data['point']['state'][3] != 0) and (cwp123_num > 0 and cwp45_num > 0 and cwp123_num + cwp45_num >= data['boundary']['cwp_num']['low_limit'])):
                    potential_actions.append(action_tuple)
        return set(potential_actions)
