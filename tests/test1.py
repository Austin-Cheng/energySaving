

graph = {
    '1#chiller': [
        '1#cdp',
        '2#cdp',
        '3#cdp',
        '1#cwp',
        '2#cwp',
        '3#cwp',
    ],
    '2#chiller': [
        '1#cdp',
        '2#cdp',
        '3#cdp',
        '1#cwp',
        '2#cwp',
        '3#cwp',
    ],
    '3#chiller': [
        '4#cdp',
        '5#cdp',
        '4#cwp',
        '5#cwp',
    ],
    '1#cdp': [
        '1#ct',
        '2#ct',
        '3#ct'
    ],
    '2#cdp': [
        '1#ct',
        '2#ct',
        '3#ct'
    ],
    '3#cdp': [
        '1#ct',
        '2#ct',
        '3#ct'
    ],
    '4#cdp': [
        '1#ct',
        '2#ct',
        '3#ct'
    ],
    '5#cdp': [
        '1#ct',
        '2#ct',
        '3#ct'
    ]
}


device_info = {
    '1#chiller': {
        'is_fault': False,
        'usable': False
    },
    '2#chiller': {
        'is_fault': False,
        'usable': False
    },
    '3#chiller': {
        'is_fault': False,
        'usable': False
    },
    '1#cwp': {
        'is_fault': False,
        'usable': False
    },
    '2#cwp': {
        'is_fault': False,
        'usable': False
    },
    '3#cwp': {
        'is_fault': False,
        'usable': False
    },
    '4#cwp': {
        'is_fault': True,
        'usable': False
    },
    '5#cwp': {
        'is_fault': True,
        'usable': False
    },
    '1#cdp': {
        'is_fault': False,
        'usable': False
    },
    '2#cdp': {
        'is_fault': False,
        'usable': False
    },
    '3#cdp': {
        'is_fault': False,
        'usable': False
    },
    '4#cdp': {
        'is_fault': True,
        'usable': False
    },
    '5#cdp': {
        'is_fault': True,
        'usable': False
    },
    '1#ct': {
        'is_fault': False,
        'usable': False
    },
    '2#ct': {
        'is_fault': False,
        'usable': False
    },
    '3#ct': {
        'is_fault': False,
        'usable': False
    },
}


def dfs(start, visited=None):
    visited.add(start)
    # 已经遍历到了叶子节点，说明是通路
    if start not in graph:
        device_info[start]['usable'] = not device_info[start]['is_fault']
    else:

        # 非叶子节点则继续遍历
        for neighbour in graph[start]:
            # 故障设备不探索
            if device_info[neighbour]['is_fault']:
                continue

            # 已经探索过的设备不探索
            if neighbour in visited:
                device_info[start]['usable'] = device_info[neighbour]['usable'] or device_info[start]['usable']
                continue

            # 继续探索
            dfs(neighbour, visited)
            device_info[start]['usable'] = device_info[neighbour]['usable'] or device_info[start]['usable']


# 从所有的 chiller 节点开始遍历
chillers = ['1#chiller', '2#chiller', '3#chiller']
visited = set()

for chiller in chillers:
    dfs(chiller, visited)

for device, info in device_info.items():
    print(device, info['usable'])
