"""
装饰器列表
"""


def fairyproperty(verbose_name='', field_type='Char'):
    """
    通用的属性装饰器，适合使用在模型中，主要是用来做序列化使用

    因为还要识别此方法的 is_fairy_property_field 属性是否为真，
    所以不能直接访问获得具体的数据

    class Person:

        @fairyproperty('年龄', 'int')
        def age(self):
            return 23

    instance = Spam()

    使用时取值时 instance.age.value

    注意：instance.age 得到的是一个描述器
    """

    class Property:
        """属性类装饰器"""

        def __init__(self, fget, **kwargs):
            # 函数
            self.fget = fget
            # 属性字段名称
            self.verbose_name = verbose_name
            # 属性字段类型
            self.field_type = field_type
            # 模型对象实例
            self._instance = None
            # 标识这是一个计算属性字段
            self.is_fairy_property_field = True

        def __get__(self, instance, cls):
            self._instance = instance
            return self

        def __call__(self):
            # 获取数据
            if self.fget is not None:
                return self.fget(self._instance)

    return Property


def fairyaction(**kwargs):
    """
    动作装饰器, 改变函数的某些行为，例如可以针对函数这是函数级别的权限类等等

    @fairyaction(permission_classes=[AllowAny])
    def list_enhance(self, view, request, *args, **kwargs):
        return view.fairy_pure_list(request, *args, **kwargs)
    """

    def decorator(func):
        if kwargs:
            for key, value in kwargs.items():
                setattr(func, key, value)
        return func

    return decorator
