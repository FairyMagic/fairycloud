"""
访问端使用的常量列表

例如客户端和管理端，或者其他端传递数据的标准

常量命名格式为 FAIRY_CALLED_{名称}
"""


"""
请求端传入 fairycloud 的命名空间

即过滤条件，展示字段等等，即跟业务数据无关的都会放到此命名空间下

例如，客户端传进来的数据格式为：

{
    'fairycloud': {
        'display_fields': ['id'. 'name'],
        'filters': [
            {field: id, operator: '=', value: 2},
            ...
        ]
        ...
    },
    data: 具体的业务数据
}
"""
FAIRY_CALLED_NAMESPACE = 'fairycloud'

"""
接口请求返回展示的字段

数据格式列表：['id', 'name', {'user': ['nick_name']}]
"""
FAIRY_CALLED_DISPLAY_FIELDS = 'display_fields'

"""客户端传入过滤条件的命名空间

通过此进行数据过滤和筛选

支持的方法：如果在 body 中传入过滤条件都支持
数据格式 List:

    [
        {
            'field': 字段名,
            'operator': 运算符,
            'value': 值,
            'type': object_property 默认为空
        },
        ...
    ]
"""
FAIRY_CALLED_QUERY_FILTERS = 'filters'

"""
函数声明：云函数或者批量函数的名称
"""
FAIRY_CALLED_FUNC_NAME = 'func_name'

"""
访问端传入使用导出配置中的哪个索引 Key
"""
FAIRY_CALLED_EXPORT_DATA_KEY = 'export_file'
