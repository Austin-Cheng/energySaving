import numpy as np
from itertools import product
from collections import deque
import json
from pandas.api.types import is_scalar
import math
from errors import BasicError


def is_nan(x):
    if x is None or np.isnan(x) or x is None or math.isnan(x):
        return True
    return False


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.int64, np.float64)):
            return int(obj) if isinstance(obj, np.int64) else float(obj)
        elif is_scalar(obj) and isinstance(obj, np.generic):
            return obj.item()
        return super(NumpyEncoder, self).default(obj)


def multi_range(args):
    ranges = []
    for arg in args:
        name = list(arg.keys())[0]
        start = arg[name]['start']
        end = arg[name]['end']
        step = arg[name]['step']
        current_range = np.arange(start, end + step, step)
        current_range = np.round(current_range, decimals=2)
        ranges.append(current_range)
    space = list(product(*ranges))
    return space


def topological_sort(graph):
    in_degree = {node: 0 for node in graph}

    for nodes in graph.values():
        for node in nodes:
            in_degree[node] += 1

    queue = deque([node for node in in_degree if in_degree[node] == 0])

    result = []

    while queue:
        current_node = queue.popleft()
        result.append(current_node)

        for next_node in graph[current_node]:
            in_degree[next_node] -= 1
            if in_degree[next_node] == 0:
                queue.append(next_node)

    if len(result) != len(graph):
        return 'Graph has a cycle, cannot perform topological sort.'

    return result


def build_graph(info):
    graph = {node: [] for node in info['agents'].keys()}
    for link in info['agent_links']:
        from_node = link['from']
        to_node = link['to']
        graph[from_node].append(to_node)
    return dict(graph)


def discrete(x, step, min_val=None, max_val=None):
    if is_nan(x):
        return None
    if x < min_val:
        x = min_val
    if x > max_val:
        x = max_val
    x = round(x / step) * step
    return round(x, 2)


def gen_state(data, state_args):
    data['point']['state'] = []
    for arg_info in state_args:
        arg_name = list(arg_info.keys())[0]
        arg_value = discrete(
            data['point'][arg_name],
            arg_info[arg_name]['step'],
            arg_info[arg_name]['start'],
            arg_info[arg_name]['end']
        )
        data['point']['state'].append(arg_value)
    data['point']['state'] = tuple(data['point']['state'])


def gen_action(data, action_args):
    data['point']['action'] = []
    for arg_info in action_args:
        arg_name = list(arg_info.keys())[0]
        arg_value = discrete(
            data['point'][arg_name],
            arg_info[arg_name]['step'],
            arg_info[arg_name]['start'],
            arg_info[arg_name]['end']
        )
        data['point']['action'].append(arg_value)
    data['point']['action'] = tuple(data['point']['action'])


def gen_state_action(data, action_args, state_args):
    gen_action(data, action_args)
    gen_state(data, state_args)
