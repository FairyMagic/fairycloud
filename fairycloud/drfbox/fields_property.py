import inspect
from rest_framework import fields


class PropertyFieldMixin:
    """计算字段业务"""

    def to_representation(self, value):
        """
        注意：这里的 value 是一个描述器
        """
        return super().to_representation(value())


def get_fairy_property_field_trans_drf_field(field_type):
    """
    根据指定的计算字段类型，动态构建对应的序列化字段

    使用 fairyproperty 装饰的类属性，找到序列化时对应 DRF 的字段类
    """
    class_name = f'{field_type}Field'
    field_class = getattr(fields, class_name, fields.CharField)
    return type(class_name, (PropertyFieldMixin, field_class), {})


def get_model_fairy_property_fields(model):
    """
    获取模型中使用 fairyproperty 装饰的方法列表
    """
    result = {}

    for name, method in inspect.getmembers(model, predicate=inspect.ismethoddescriptor):
        if not name.startswith('__') and getattr(
            method, 'is_fairy_property_field', False
        ):
            result[name] = method
    return result
