from algorithm.agents.q_learning_agents.Q_Matrix import QMatrix
from algorithm.agents.q_learning_agents.Q_Learning import QLearningAgent
from cfg import agents_info, matrix_path


if __name__ == '__main__':
    realtime_data = [{}, {}]
    for agent_name, agent_info in agents_info['agents'].items():
        # 初始化
        print(f"{agent_name} initializing")
        q_matrix = QMatrix(
            agent_name,
            agent_info['state_args'],
            agent_info['action_args'],
            agent_info['reward_args'],
            agent_info['initial_value'],
            from_file=True
        )

        # 训练
        print(f"{agent_name} training")
        agent = QLearningAgent(q_matrix)
        for i, rd in enumerate(realtime_data):
            rd['action'] = [rd[arg] for arg in q_matrix.action_args_name]
            rd['state'] = [rd[arg] for arg in q_matrix.state_args_name]
            rd['reward'] = rd[q_matrix.reward_arg_name]

        agent.update_q_value(
            reward=realtime_data[1][q_matrix.reward_arg_name],
            current_data=realtime_data[1],
            last_data=realtime_data[0]
        )

        q_matrix.save_matrix(matrix_path)
