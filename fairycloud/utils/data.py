"""
数据处理工具函数
"""
from collections import Mapping
from pydash import objects


def dict_merge(origin_dict, merge_dict):
    """递归合并字典

    注意：如果是不可变对象，merge_dict 中的值会覆盖 origin_dict 中对应的值

    Params:
        origin_dict dict 源字典
        merge_dict dict 待合并的字典
    """
    for key, _ in merge_dict.items():
        if (
            key in origin_dict
            and isinstance(origin_dict[key], dict)
            and isinstance(merge_dict[key], Mapping)
        ):
            dict_merge(origin_dict[key], merge_dict[key])
        else:
            origin_dict[key] = merge_dict[key]
    return origin_dict


def generate_nest_dict(fields):
    """生成嵌套的字典

    例如：abc.allen.girl 将会处理成

    {
        'abc': {
            'allen': {
                'girl': {}
            }
        }
    }
    """
    tree_dict = {}
    for key in reversed(fields.split('.')):
        tree_dict = {key: tree_dict}
    return tree_dict


def get_prefetch_fields(data=None):
    """获取 prefetch_related 字段

    例如客户端传入的字段是：['id', 'age', {'user': ['ss', {'work': ['address']}]}]

    返回的结果是 user.work

    Param:
        data list display_fields
    """
    if not data:
        return

    prefetch_keys, removed_keys = set(), set()

    def clean_keys(data, defaultk=''):
        for _, item in enumerate(data):
            if isinstance(item, dict):
                if defaultk:
                    removed_keys.add(defaultk)
                for key, value in item.items():
                    connect_key = f'{defaultk}.{key}' if defaultk else key
                    if isinstance(value, list):
                        clean_keys(value, connect_key)
            elif defaultk:
                prefetch_keys.add(defaultk)

    clean_keys(data)
    return list(prefetch_keys.difference(removed_keys))


def generate_nest_field_dict(data, result=None):
    """
    生成嵌套的字段字典

    s = ['id', 'age', {'user': ['ss', {'work': ['address']}]}]

    返回的结果如下：

    {
        'id': 'id',
        'age': 'age',
        'user': {
            'ss': 'ss',
            'work': {
                'address': 'address'
            }
        }
    }
    """
    result = {} if result is None else result
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                result[key] = {}
                generate_nest_field_dict(value, result[key])
        else:
            result[item] = item
    return result


def check_include_nest_dict(data):
    """
    检测字典中是否包含嵌套的字典数据

    {
        1: 2,
        2: 3,
        3: {}
    }
    这个时候返回 True
    """
    result = False

    for _, value in data.items():
        if isinstance(value, dict):
            result = True
            break
    return result


def get_data_from_dict(out_data, key):
    """从字典中获取对应的数据

    Params:
        out_data dict 数据
        key string 以点号连接的键

    Returns:
        list

    {
        'age': [
            {"staff": {"u": [{"mm": 45}]}},
            {"staff": {"u": [{"mm": 46}]}}
        ]
    }

    key 为 'age.staff.u.mm' 时

    处理后返回 [45, 46]
    """
    if not key or not out_data:
        return

    result = []
    key_split = key.split('.')

    def inner_hand(data, index):
        key = key_split[index]
        value = objects.get(data, key)

        if index == (len(key_split) - 1):
            if value is not None:
                result.append(str(value))
            return

        if isinstance(value, list):
            k_index = index + 1
            for item in value:
                inner_hand(item, k_index)
        else:
            inner_hand(value, index + 1)

    inner_hand(out_data, 0)
    return result
