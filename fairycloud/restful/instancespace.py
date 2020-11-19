"""
视图对象 Fairy 对象空间实例
"""

"""默认合法的键和默认值，注意这个字典不能更改"""

DEFAULT_SPACE = {
    # 应用名称
    'app_label': None,
    # 由自定义在顶级命名空间内和应用空间的视图对象合并新构造的视图对象
    'custom_view_instance': None,
    # 对应自定义动作的函数处理器
    'custom_action_handler': None,
    # 展示字段，即返回给客户端的数据
    'display_fields': None,
    # 扩展字段
    'expand_fields': None,
    # 导出的配置
    'export_config': None,
    # 模型
    'model': None,
    # 模型名称
    'model_label': None,
    # 客户端传入的 fairycloud 对应的请求数据，都放到此命名空间中
    # 约定客户端传入的数据分为两部分
    # {
    #   fairycloud: {},
    #   data: {}
    # }
    'request_namespace': None,
    # 配置声明类
    'statements_class': None,
    # 扩展字段是否已经转换过
    'transform_expand_fields': None,
}


class FairyInstance:
    """
    承载全部自定义添加的属性
    """

    # 对象空间实例属性名称
    instance_namespace = 'fairy_instance'

    def __init__(self):
        """
        初始化属性
        """
        for key, value in DEFAULT_SPACE.items():
            setattr(self, key, value)

    def __setattr__(self, name, value):
        if name not in DEFAULT_SPACE:
            raise Exception(f'设置键： {name} 不合法')
        return super().__setattr__(name, value)

    @classmethod
    def set_namespace_instance(cls, view):
        """设置命名空间对象"""
        setattr(view, cls.instance_namespace, cls())
