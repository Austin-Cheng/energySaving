from algorithm.agents.q_learning_agents.Q_Matrix import QMatrix
from algorithm.agents.q_learning_agents.Q_Learning import QLearningAgent
from cfg import agents_info, matrix_path, data_path, epoches
import pandas as pd
import os
from utilities.utils import gen_state_action
from read_data_copy import read_latest_point_data


history_df_1 = pd.read_excel(os.path.join(data_path, 'final_1.xlsx'), index_col=0, parse_dates=[0])
history_df_2 = pd.read_excel(os.path.join(data_path, 'final_2.xlsx'), index_col=0, parse_dates=[0])
history_df_3 = pd.read_excel(os.path.join(data_path, 'final_3.xlsx'), index_col=0, parse_dates=[0])

history_df_joined = pd.merge(history_df_1, history_df_2, left_index=True, right_index=True, how='inner')
history_df_joined = pd.merge(history_df_joined, history_df_3, left_index=True, right_index=True, how='inner')
history_df_joined['ct_out_temperature'] = history_df_joined['ct_out_temperature'] + history_df_joined['outdoor_wet_temperature']
history_df_joined = history_df_joined[['mean_plr', 'ct_out_temperature', 'chr_1_state', 'chr_2_state', 'chr_3_state', 'cds_cop', 'chiller_supply_temperature']]

history_df_joined.to_excel(os.path.join(data_path, 'final_joined.xlsx'), index=True)
history_df_joined = history_df_joined[list(read_latest_point_data().keys())]
history_df_joined = history_df_joined.rename(columns={
        'outdoor_wet_temperature': 'ChilledWaterSystem_OutdoorWetBulbTemperature',
        'chr_12_num': 'GcChillerNumber_12_ChillerNumberFeedback',
        'chr_3_num': 'GcChillerNumber_3_ChillerNumberFeedback',
        'cds_cooling': 'ChilledWaterSystem_ChilledWaterSideColdLoad',
        'cls_cooling': 'ChilledWaterSystem_CoolingWaterSideColdLoad',
        'cds_cop': 'ChilledWaterSystem_ChilledWaterSideCOP',
        'cls_cop': 'ChilledWaterSystem_CoolingWaterSideCOP',
        'chr_1_fault': 'Chiller_1_NbFaultStatus',
        'chr_2_fault': 'Chiller_2_NbFaultStatus',
        'chr_3_fault': 'Chiller_3_NbFaultStatus',
        'chr_1_mode': 'Chiller_1_ManualAutomatic',
        'chr_2_mode': 'Chiller_2_ManualAutomatic',
        'chr_3_mode': 'Chiller_3_ManualAutomatic',
        'chr_1_state': 'Chiller_1_NbRunningStatus',
        'chr_2_state': 'Chiller_2_NbRunningStatus',
        'chr_3_state': 'Chiller_3_NbRunningStatus',
        'cls_delta_temperature': 'MainCoolingWater_WaterDifferentialTemperatureFeedback',
        'ct_out_temperature': 'GcCoolingTowerTempreture_CoolingTowerTempretureFeedback',
        'cdp_123_num': 'GcCoolingWaterPumpNumber_123_CoolingWaterPumpNumberFeedback',
        'cdp_45_num': 'GcCoolingWaterPumpNumber_45_CoolingWaterPumpNumberFeedback',
        'mpp_cdp_water_fluid': 'MainCoolingWater_Flow',
        'ct_123_num': 'GcCoolingTowerNumber_CoolingTowerNumberFeedback',
        'cwp_123_num': 'GcChilledWaterPumpNumber_123_ChilledWaterPumpNumberFeedback',
        'cwp_45_num': 'GcChilledWaterPumpNumber_45_ChilledWaterPumpNumberFeedback',
        'delta_press': 'MainChilledWater_WaterDifferentialPressureFeedback',
        'chiller_supply_temperature': 'GcChillerTempreture_ChillerTempretureFeedback',
        'mean_plr': 'ChilledWaterSystem_ChillerLoadRate',
        'cds_delta_temperature': 'MainChilledWater_WaterDifferentialTemperatureFeedback'
})
history_df_joined.to_csv('history_point_data.csv')

history_data = []
for d in history_df_joined.to_dict(orient='records'):
    history_data.append({'point': d})


if __name__ == '__main__':
    # history_data = []

    for agent_name, agent_info in agents_info['agents'].items():
        # 初始化
        print(f"{agent_name} initializing")
        matrix = QMatrix(
            agent_name,
            agent_info['state_args'],
            agent_info['action_args'],
            agent_info['reward_arg'],
            agent_info['initial_value'],
            from_file=False
        )
        # matrix.save_matrix(matrix_path)

        # 训练
        print(f"{agent_name} training")
        agent = QLearningAgent(matrix)
        for epoch in range(epoches):
            for i, hd in enumerate(history_data):
                # hd['action'] = [hd[arg] for arg in matrix.action_args_name]
                # hd['state'] = [hd[arg] for arg in matrix.state_args_name]
                hd['point']['reward'] = hd['point'][matrix.reward_arg_name]
                gen_state_action(hd, matrix.action_args, matrix.state_args)
                if i == 0:
                    continue
                agent.update_q_value(
                    current_data=hd,
                    last_data=history_data[i-1]
                )

        matrix.save_matrix(matrix_path)
