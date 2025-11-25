import json
import os
from cfg import cfg_path
import re


point_map = json.load(open(os.path.join(cfg_path, 'point_mappings.json'), 'r', encoding='UTF-8'))


class AFUColdSomeAction:
    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        cold_inds = []
        for i, arg_name in enumerate(data['agent']['action_args_name']):
            if data['switch'][re.sub(r'Feedback$', 'Control', arg_name)] == 'off':
                cold_inds.append(i)

        for nominal_action in data['agent']['action_space']:
            for ind in cold_inds:
                if data['agent']['action_space'][ind] != data['point']['action'][ind]:
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
                if nominal_action in actions:
                    actions.remove(nominal_action)
                print(f'remove action by AFUChrNumByLocalMode: {nominal_action}')
            if data['point'][point_map['chr_1_mode']] == 0 and data['point'][point_map['chr_2_mode']] == 0 and nominal_action[0] != int(data['point'][point_map['chr_1_state']] or data['point'][point_map['chr_2_state']]):
                if nominal_action in actions:
                    actions.remove(nominal_action)
            if data['point'][point_map['chr_1_mode']] == 0 and data['point'][point_map['chr_1_state']] == 1 and nominal_action[0] != 1:
                if nominal_action in actions:
                    actions.remove(nominal_action)
            if data['point'][point_map['chr_2_mode']] == 0 and data['point'][point_map['chr_2_state']] == 1 and nominal_action[0] != 1:
                if nominal_action in actions:
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

    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        if data['point'][point_map['chr_12_num']] is None or data['point'][point_map['chr_3_num']] is None:
            return set()

        if data['point'][point_map['chr_12_num']] == 0:
            for action in data['agent']['action_space']:
                if action[0] != 0:
                    if action in actions:
                        actions.remove(action)
        if data['point'][point_map['chr_3_num']] == 0:
            for action in data['agent']['action_space']:
                if action[1] != 0:
                    if action in actions:
                        actions.remove(action)
        if data['point'][point_map['chr_12_num']] != 0 or data['point'][point_map['chr_3_num']] != 0:
            actions.remove((0, 0))
        return actions


class AFUCtNumByChrNum:
    DESCRIPTION = """
        考虑冷却泵和主机的绑定关系。
    """

    @classmethod
    def filter(cls, data):
        actions = set(data['agent']['action_space'])

        if data['point'][point_map['chr_12_num']] is None or data['point'][point_map['chr_3_num']] is None:
            return set()

        if data['point'][point_map['chr_12_num']] != 0 or data['point'][point_map['chr_3_num']] != 0:
            actions.remove((0,))

        if data['point'][point_map['chr_12_num']] == 0 and data['point'][point_map['chr_3_num']] == 0:
            actions = {(0,)}
        return actions


class AFUChrSupplyTemp:
    DESCRIPTION = """
    
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
        if not potential_actions:
            return set(data['point']['action'])
        return set(potential_actions)


class AFUCWS:
    DESCRIPTION = """
        压差调节幅度限制
        冷机关联限制
    """

    @classmethod
    def filter(cls, data):
        potential_actions = []
        for action_tuple in data['agent']['action_space']:
            cwp123_num, cwp45_num, pres_diff = action_tuple
            last_pres_diff = data['last_point'][point_map['delta_press']]
            if abs(pres_diff - last_pres_diff) <= data['boundary']['delta_press']['max_step']:
                if ((data['point'][point_map['chr_12_num']] == 0 and data['point'][point_map['chr_3_num']] == 0) and (cwp123_num + cwp45_num == data['boundary']['cwp_num']['low_limit'])) or \
                        ((data['point'][point_map['chr_12_num']] == 0 and data['point'][point_map['chr_3_num']] != 0) and (cwp123_num == 0 and cwp45_num > 0 and cwp45_num >= data['boundary']['cwp_num']['low_limit'])) or \
                        ((data['point'][point_map['chr_12_num']] != 0 and data['point'][point_map['chr_3_num']] == 0) and (cwp123_num > 0 and cwp123_num >= data['boundary']['cwp_num']['low_limit'] and cwp45_num == 0)) or \
                        ((data['point'][point_map['chr_12_num']] != 0 and data['point'][point_map['chr_3_num']] != 0) and (cwp123_num > 0 and cwp45_num > 0 and cwp123_num + cwp45_num >= data['boundary']['cwp_num']['low_limit'])):
                    potential_actions.append(action_tuple)
        return set(potential_actions)
