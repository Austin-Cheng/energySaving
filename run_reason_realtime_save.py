from cfg_save import agents_info, dp_funcs, plc_funcs, ratings, reason_start_step, actions_switch_info
from utilities.utils import topological_sort
from algorithm.agents.q_learning_agents.Q_Matrix import QMatrix
from algorithm.agents.q_learning_agents.Q_Learning import QLearningAgent
from copy import deepcopy
from read_data_copy import read_latest_point_data, read_dynamic_data, read_action_switch_data
import time
from utilities.utils import gen_state_action, build_graph, gen_state
import pandas as pd


if __name__ == '__main__':
    graph = build_graph(agents_info)
    sorted_agent = topological_sort(graph)

    last_data_for_reason_schedule = None
    last_data = None
    current_data = None

    agents_map = {}
    for agent_name in sorted_agent:
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

    results = []
    for i, point_data in enumerate(read_latest_point_data()):
        if point_data['time'] == '2024-10-04 01:40:00':
            print(point_data)
        print(i)
        if i == 16:
            print(i)
        # print(point_data)
        # start_time = time.time()
        # while last_data and time.time() - start_time < 60:
        #     time.sleep(1)

        last_data = current_data
        current_data = {
            'point': point_data,
            'last_point': last_data['point'] if last_data else None,
            'switch': read_action_switch_data(),
            'boundary': read_dynamic_data(),
            'rating': ratings,
        }

        if last_data is None:
            continue

        # for agent_name in sorted_agent:
        #     print(f'{agent_name} training')
        #     agent = agents_map[agent_name]
        #
        #     current_data_copy = deepcopy(current_data)
        #
        #     current_data['point']['reward'] = current_data['point'][agent.qm.reward_arg_name]
        #     gen_state_action(current_data, agent.qm.action_args, agent.qm.state_args)
        #     gen_state_action(last_data, agent.qm.action_args, agent.qm.state_args)
        #
        #     agent.update_q_value(
        #         current_data=current_data,
        #         last_data=last_data
        #     )

        step += 1

        if last_data_for_reason_schedule and abs(current_data['point']['cds_cooling'] - last_data_for_reason_schedule['point']['cds_cooling']) < 100 and abs(current_data['point']['outdoor_wet_temperature'] - last_data_for_reason_schedule['point']['outdoor_wet_temperature']) < 1:
            continue

        outputs = {}
        for agent_name in sorted_agent:
            print(f'{agent_name} reasoning')
            if agent_name == 'chiller_supply_temperature_agent':
                print('chr_supply_temperature')
            agent = agents_map[agent_name]

            current_data_copy = deepcopy(current_data)

            current_data_copy['agent'] = {
                'action_space': agent.qm.action_space,
                'action_args_name': agent.qm.action_args_name
            }

            for link in agents_info['agent_links']:
                if link['to'] == agent_name:
                    for para in link['inter_paras']:
                        if current_data['switch'][para] == 'on':
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
            print(output)
            outputs.update(output)
            # outputs.update({a: current_data_copy['point'][a] for a in agent.qm.state_args_name})
            # outputs.update({agent.qm.reward_arg_name: current_data_copy['point'][agent.qm.reward_arg_name]})
            outputs['time'] = point_data['time']

        last_data_for_reason_schedule = current_data

        print(outputs)
        results.append(outputs)

    print(results)
    results = pd.DataFrame(results)
    results['time'] = pd.to_datetime(results['time'])
    results.set_index('time', inplace=True)
    results.sort_index(inplace=True)
    results = results.resample('5T').ffill()
    print(results.head())
    results.to_excel('result.xlsx')
