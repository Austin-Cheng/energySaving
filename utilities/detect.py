import importlib.util
import os
import sys
import inspect


def get_classes_from_file(file_path):
    # 获取文件的绝对路径
    abs_file_path = os.path.abspath(file_path)

    # 获取文件所在的目录和文件名（不带扩展名）
    dir_name, file_name = os.path.split(abs_file_path)
    module_name, _ = os.path.splitext(file_name)

    # 创建一个模块规范
    spec = importlib.util.spec_from_file_location(module_name, abs_file_path)

    # 从规格创建并加载模块
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 获取模块中的所有类
    class_names = {name: obj for name, obj in inspect.getmembers(module) if inspect.isclass(obj) and obj.__module__ == module.__name__}

    return class_names


def get_functions_from_file(file_path):
    # 确保文件存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # 获取文件所在的目录和文件名（不带扩展名）
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)

    # 将文件所在目录添加到 sys.path 以支持相对导入
    file_dir = os.path.dirname(file_path)
    if file_dir not in sys.path:
        sys.path.append(file_dir)

    # 执行模块，使其生效
    spec.loader.exec_module(module)

    # 使用 inspect 查找模块中的所有函数
    functions_dict = {name: obj for name, obj in inspect.getmembers(module) if inspect.isfunction(obj) and obj.__module__ == module_name}

    return functions_dict
