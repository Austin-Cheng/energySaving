from algorithm.agents.q_learning_agents.Q_Matrix import QMatrix
from algorithm.agents.q_learning_agents.Q_Learning import QLearningAgent
from cfg import agents_info, matrix_path, epoches, logger, basic_cfg
from utilities.utils import gen_state_action
from read_data import requestor
import time
from collections import defaultdict
from tqdm import tqdm


if __name__ == '__main__':

    st = time.time()
    history_data = requestor.read_history_point_data()
    history_data = [{'point': hd} for hd in history_data]

    for tp in basic_cfg['timePeriods']:
        logger.info(f'history training - time period - {tp["startTime"]} - {tp["endTime"]}')
    logger.info(f'history training - time granularity - {basic_cfg["timeGranularity"]}')
    logger.info(f'history training - epoches - {epoches}')
    logger.info(f'history training - total data number - {len(history_data)}')

    # count_map = defaultdict(int)
    for agent_name, agent_info in tqdm(agents_info['agents'].items()):
        # 初始化
        matrix = QMatrix(
            agent_name,
            agent_info['state_args'],
            agent_info['action_args'],
            agent_info['reward_arg'],
            agent_info['initial_value'],
            from_file=False
        )

        # 训练
        agent = QLearningAgent(matrix)
        count = 0
        for epoch in tqdm(range(epoches)):
            for i, hd in history_data:
                hd['point']['reward'] = hd['point'][matrix.reward_arg_name]
                gen_state_action(hd, matrix.action_args, matrix.state_args)
                if i == 0:
                    continue
                res = agent.update_q_value(current_data=hd, last_data=history_data[i-1])
                logger.info(f'history training - {agent_name} - {hd["point"]["time"]} - {res}')

        logger.info(f'history training - valid data num - {agent_name} - {round(count/epoches, 0)}')
        matrix.save_matrix(matrix_path)

    et = time.time()
    logger.info(f'history training - cost time(minute) - {round((et - st)/60, 1)}')
