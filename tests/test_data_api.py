import mmap
import json


with open('/opt/data/python/energy-saving/mmap/mmap', 'r+') as f:
    # 将文件映射到内存中
    mm = mmap.mmap(f.fileno(), 0)  # 0表示映射整个文件
    try:
        # 读取整个文件内容
        content = mm.read().decode('utf-8')
        lines = content.split('\n')
        for line in lines:
            for point in line.split(','):
                print(point)
    finally:
        # 确保关闭mmap对象
        mm.close()


# import pandas as pd
# import mmap
#
# # 打开文件
# with open('/opt/data/python/energy-saving/mmap/mmap', 'r+b') as f:
#     # 创建 mmap 对象
#     mmapped_file = mmap.mmap(f.fileno(), 0)
#
#     # 使用 pandas 读取 mmap 对象
#     df = pd.read_csv(mmapped_file)
#
#     # 显示前 5 行数据
#     print(df.head())
#     print(df.tail())
