import numpy as np
import pandas as pd
from utilities.utils import multi_range
import os
from cfg import matrix_path


class QMatrix:
    def __init__(self, name: str, state_args, action_args, reward_arg, initial_value, from_file=False):
        self.name = name
        self.state_args = state_args
        self.action_args = action_args
        self.reward_arg = reward_arg
        self.initial_value = initial_value

        self.state_args_name = [list(arg.keys())[0] for arg in self.state_args]
        self.action_args_name = [list(arg.keys())[0] for arg in self.action_args]
        self.reward_arg_name = reward_arg

        self.state_space = multi_range(self.state_args)
        self.action_space = multi_range(self.action_args)

        if not from_file:
            self.q_matrix = self.build_matrix(self.action_space, self.state_space, initial_value)
            self.step_matrix = self.build_matrix(self.action_space, self.state_space, 1)
        else:
            self.q_matrix = self.build_matrix_from_file(os.path.join(matrix_path, 'q_' + name + '.xlsx'))
            self.step_matrix = self.build_matrix_from_file(os.path.join(matrix_path, 'step_' + name + '.xlsx'))

    @staticmethod
    def build_matrix_from_file(file_name):
        df = pd.read_excel(file_name, index_col=0)
        df.index = df.index.map(eval)
        df.columns = df.columns.map(eval)
        return df

    @staticmethod
    def build_matrix(action_space, state_space, initial_value):
        data = np.full((len(action_space), len(state_space)), initial_value)
        columns = pd.MultiIndex.from_tuples(state_space)
        index = pd.MultiIndex.from_tuples(action_space)
        df = pd.DataFrame(data, columns=columns, index=index)
        return df

    def save_matrix(self, file_path):
        self.q_matrix.index = self.q_matrix.index.map(str)
        self.q_matrix.columns = self.q_matrix.columns.map(str)
        self.q_matrix.to_excel(os.path.join(file_path, f'q_{self.name}.xlsx'))

        self.step_matrix.index = self.step_matrix.index.map(str)
        self.step_matrix.columns = self.step_matrix.columns.map(str)
        self.step_matrix.to_excel(os.path.join(file_path, f'step_{self.name}.xlsx'))
