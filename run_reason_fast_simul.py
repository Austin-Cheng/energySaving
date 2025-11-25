from cfg import agents_info, dp_funcs, plc_funcs, ratings, reason_start_step
from utilities.utils import topological_sort
from algorithm.agents.q_learning_agents.Q_Matrix import QMatrix
from algorithm.agents.q_learning_agents.Q_Learning import QLearningAgent
from copy import deepcopy
from read_data import requestor
import time
from utilities.utils import gen_state_action, build_graph
from errors import BasicError
from cfg import logger
from datetime import datetime
import re
from tqdm import tqdm


if __name__ == '__main__':
    try:
        graph = build_graph(agents_info)
        sorted_agent = topological_sort(graph)

        last_data_for_reason_schedule = None
        last_data = None
        current_data = None

        agents_map = {}
        for agent_name in tqdm(sorted_agent):
            matrix = QMatrix(
                name=agent_name,
                state_args=agents_info['agents'][agent_name]['state_args'],
                action_args=agents_info['agents'][agent_name]['action_args'],
                reward_arg=agents_info['agents'][agent_name]['reward_arg'],
                initial_value=agents_info['agents'][agent_name]['initial_value'],
                from_file=True
            )

            agent = QLearningAgent(matrix)
            agents_map[agent_name] = agent

        step = reason_start_step

        while True:
            # start_time = time.time()
            # while last_data and time.time() - start_time < 300:
            #     time.sleep(1)

            last_data = current_data
            current_data = {
                'point': requestor.read_latest_point_data(),
                'last_point': last_data['point'] if last_data else None,
                'switch': requestor.read_action_switch_data(),
                'boundary': requestor.read_dynamic_data(),
                'rating': ratings,
            }
            # current_data['point']['ChilledWaterSystem_ChilledWaterSideColdLoad'] = 676.83

            if last_data is None:
                continue

            outputs = {}
            for agent_name in sorted_agent:
                print(f'{agent_name} training')
                agent = agents_map[agent_name]

                current_data_copy = deepcopy(current_data)

                current_data['point']['reward'] = current_data['point'][agent.qm.reward_arg_name]
                gen_state_action(current_data, agent.qm.action_args, agent.qm.state_args)
                gen_state_action(last_data, agent.qm.action_args, agent.qm.state_args)

                res = agent.update_q_value(
                    current_data=current_data,
                    last_data=last_data
                )
                logger.info(f'realtime training - {agent_name} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {current_data["point"]["time"]} - {res}')

            step += 1

            if last_data_for_reason_schedule and current_data['point']['ChilledWaterSystem_ChilledWaterSideColdLoad'] <= 50 and abs(current_data['point']['ChilledWaterSystem_ChilledWaterSideColdLoad'] - last_data_for_reason_schedule['point']['ChilledWaterSystem_ChilledWaterSideColdLoad']) < 100 and abs(current_data['point']['ChilledWaterSystem_OutdoorWetBulbTemperature'] - last_data_for_reason_schedule['point']['ChilledWaterSystem_OutdoorWetBulbTemperature']) < 1:
                continue

            for agent_name in sorted_agent:
                print(f'{agent_name} reasoning')
                agent = agents_map[agent_name]

                current_data_copy = deepcopy(current_data)

                current_data_copy['agent'] = {
                    'action_space': agent.qm.action_space,
                    'action_args_name': agent.qm.action_args_name
                }

                for link in agents_info['agent_links']:
                    if link['to'] == agent_name:
                        for para in link['inter_paras']:
                            if current_data['switch'][re.sub(r'Feedback$', 'Control', para)]:
                                current_data_copy['point'][para] = outputs[para]

                for arg in agent.qm.state_args_name:
                    if arg == -200 or arg is None:
                        output = dict(zip(agent.qm.action_args_name, [-100] * len(agent.qm.action_args_name)))
                        outputs.update(output)
                        continue

                gen_state_action(current_data_copy, agent.qm.action_args, agent.qm.state_args)
                gen_state_action(last_data, agent.qm.action_args, agent.qm.state_args)

                dp_funcs_ = [dp_funcs[fn] for fn in agents_info['agents'][agent_name]['dps']]
                agent.data_process(current_data_copy, dp_funcs_)

                plc_funcs_ = [plc_funcs[fn] for fn in ['AFUColdSomeAction'] + agents_info['agents'][agent_name]['filters']]
                usable_action = agent.action_filter(current_data_copy, plc_funcs_)
                if usable_action:
                    output = agent.pick_action(current_data_copy, usable_action, step)
                else:
                    output = dict(zip(agent.qm.action_args_name, [-200] * len(agent.qm.action_args_name)))
                outputs.update(output)

            last_data_for_reason_schedule = current_data

            print(
                current_data["point"]["time"],
                current_data["point"]["ChilledWaterSystem_ChilledWaterSideColdLoad"],
                current_data['point']['ChilledWaterSystem_OutdoorWetBulbTemperature'],
                current_data['point']['ChilledWaterSystem_ChilledWaterSideCOP'],
                current_data['point']['ChilledWaterSystem_CoolingWaterSideCOP']
            )
            outputs['time'] = current_data['point']['time']
            outputs['batchId'] = current_data['point']['batchId']
            outputs['GcCoolingTowerTempreture_CoolingTowerTempretureFeedback'] = current_data['point']['ChilledWaterSystem_OutdoorWetBulbTemperature'] + outputs['GcCoolingTowerTempreture_CoolingTowerTempretureFeedback']
            requestor.write_action_data(outputs)
            print(outputs)
            end_time = time.time()
            logger.info(f'realtime training - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - current_data: \n {current_data} \n outputs: \n {outputs}')
    except BasicError as e:
        requestor.write_state(e)
        raise e
