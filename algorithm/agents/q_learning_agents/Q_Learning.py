import math
from .Q_Matrix import QMatrix
import datetime
import random
from cfg import a_period_steps


class QLearningAgent:
    def __init__(self, qm: QMatrix):
        self.qm = qm

        self.gamma = 0.01
        self.a_period_steps = a_period_steps

    @staticmethod
    def dynamic_alpha(step):
        alpha = 0.6 * math.exp(- 0.2 * step) + 0.2
        return alpha

    def update_q_value(self, current_data, last_data):
        reward = current_data['point']['reward']

        if current_data['point']['action'] != last_data['point']['action']:
            return False

        if current_data['point']['state'] != last_data['point']['state']:
            # print('curret state does not equal last state')
            return False

        if last_data['point']['action'] not in self.qm.action_space:
            return False

        if last_data['point']['state'] not in self.qm.state_space:
            return False

        if current_data['point']['state'] not in self.qm.state_space:
            return False

        step = self.qm.step_matrix.at[last_data['point']['action'], last_data['point']['state']]
        if step == 1:
            self.qm.q_matrix.at[last_data['point']['action'], last_data['point']['state']] = reward
        else:
            last_Q = self.qm.q_matrix.at[last_data['point']['action'], last_data['point']['state']]

            max_Q = self.qm.q_matrix[current_data['point']['state']].max()
            delta_Q = self.dynamic_alpha(step) * (reward + self.gamma * max_Q - last_Q)
            new_q = last_Q + delta_Q
            self.qm.q_matrix.at[last_data['point']['action'], last_data['point']['state']] = new_q

        self.qm.step_matrix.at[last_data['point']['action'], last_data['point']['state']] += 1

        return self.qm.q_matrix.at[last_data['point']['action'], last_data['point']['state']]

    @staticmethod
    def data_process(data, dps):
        for dp in dps:
            dp(data)

    def action_filter(self, data, filters):
        if len(filters) == 0:
            return self.qm.action_space
        useful_action = set(self.qm.action_space)
        for func in filters:
            useful_action = useful_action & func.filter(data)
        return useful_action

    def epsilon_greedy_policy(self, state, usable_action, step):
        if step > self.a_period_steps:
            step = self.a_period_steps

        q_div_p = 10 * step / self.a_period_steps

        tmp_Q = self.qm.q_matrix[self.qm.q_matrix.index.isin(usable_action)][tuple(state)]

        if len(tmp_Q) == 0:
            return None

        sum_Q = tmp_Q.sum()

        probability = tmp_Q / sum_Q / (1 + q_div_p)
        row_of_max_q = tmp_Q.idxmax()

        probability[row_of_max_q] += q_div_p / (1 + q_div_p)
        return random.choices(probability.index, weights=probability, k=1)[0]

    def max_explored_policy(self, state, usable_action, step):
        tmp_Q = self.qm.q_matrix[self.qm.q_matrix.index.isin(usable_action)][tuple(state)]

        if len(tmp_Q) == 0:
            return None

        tmp_Q = tmp_Q[tmp_Q != self.qm.initial_value]

        if len(tmp_Q) == 0:
            return self.epsilon_greedy_policy(state, usable_action, step)

        row_of_max_q = tmp_Q.idxmax()

        return row_of_max_q

    def pick_action(self, data, usable_action, step):
        # action = self.epsilon_greedy_policy(data['point']['state'], usable_action, step)
        action = self.max_explored_policy(data['point']['state'], usable_action, step)
        if action is None:
            action = [None] * len(self.qm.action_args_name)
        return dict(zip(self.qm.action_args_name, action))
