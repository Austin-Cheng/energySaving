import os
import json
from utilities.detect import get_classes_from_file, get_functions_from_file


project_path = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(project_path, "data")
matrix_path = os.path.join(data_path, "matrix")

cfg_path = os.path.join(project_path, "config")
agents_info = json.load(open(os.path.join(cfg_path, 'agents_save.json'), 'r', encoding='UTF-8'))
ratings = json.load(open(os.path.join(cfg_path, 'ratings.json'), 'r', encoding='UTF-8'))
# boundaries = json.load(open(os.path.join(cfg_path, 'dynamic_parameters.json'), 'r', encoding='UTF-8'))
actions_switch_info = json.load(open(os.path.join(cfg_path, 'action_switches.json'), 'r', encoding='UTF-8'))

plc_path = os.path.join(project_path, "plcs_save.py")
dp_path = os.path.join(project_path, "dps_save.py")

plc_funcs = get_classes_from_file(plc_path)
dp_funcs = get_functions_from_file(dp_path)

ALGORITHM_KEY = os.path.basename(os.path.normpath(project_path))

a_period_steps = 60480
reason_start_step = 44560
epoches = 5

