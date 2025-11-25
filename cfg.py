import os
import json
import logging
from utilities.detect import get_classes_from_file, get_functions_from_file


project_path = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(project_path, "data")
matrix_path = os.path.join(data_path, "matrix")
cfg_path = os.path.join(project_path, "config")
log_path = os.path.join(project_path, "log")
plc_path = os.path.join(project_path, "plcs.py")
dp_path = os.path.join(project_path, "dps.py")

agents_info = json.load(open(os.path.join(cfg_path, 'agents.json'), 'r', encoding='UTF-8'))
ratings = json.load(open(os.path.join(cfg_path, 'ratings.json'), 'r', encoding='UTF-8'))
basic_cfg = json.load(open(os.path.join(cfg_path, 'basic.json'), 'r', encoding='UTF-8'))

plc_funcs = get_classes_from_file(plc_path)
dp_funcs = get_functions_from_file(dp_path)

ALGORITHM_KEY = os.path.basename(os.path.normpath(project_path))

a_period_steps = 60480
reason_start_step = 44560
epoches = 2

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
info_handler = logging.FileHandler(os.path.join(log_path, "log_info.txt"))
info_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(formatter)
logger.addHandler(info_handler)
