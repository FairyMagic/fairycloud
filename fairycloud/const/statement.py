"""
配置声明

用户配置位置：对应模型指定端类下

命名格式：FAIRY_STATEMENT_{名称}
"""

"""
用户数据插入处理，如果模型有多个用户字段，用户根据自己的
业务需求，写自定义的业务处理

数据类型：dict

声明位置：命名空间下的对应模型指定端的 Statements 下

示例：

user_pip_config = {
    'field': 字段名,
    'action_enabled': {
        'create': True | False,
        ...
    }
}
"""
FAIRY_STATEMENT_USER_PIP_CONFIG = 'user_pip_config'

"""
是否根据当前登录的用户进行过滤

数据类型：dict

声明位置：命名空间下的对应模型指定端的 Statements 下

示例：

user_filter_config = {
    'field': 字段名,
    'action_enabled': {
        'create': True | False
    }
}

注意：针对 retrieve_mine 和 list_mine 这两种动作，默认开启根据当前登录
用户进行过滤，
"""
FAIRY_STATEMENT_USER_FILTER_CONFIG = 'user_filter_config'
