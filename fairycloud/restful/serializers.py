import copy
from collections import OrderedDict

from django.db import models

from rest_framework import serializers
from rest_framework.fields import SkipField, JSONField as DrfJsonField
from rest_framework.relations import PKOnlyObject

from fairycloud.const import FAIRY_INNER_ACTION_EXPORT_FILE
from fairycloud.drfbox import fields as drf_fields
from fairycloud.drfbox.fields_property import (
    get_fairy_property_field_trans_drf_field,
    get_model_fairy_property_fields,
)

from fairycloud.utils import meta
from fairycloud.utils.data import (
    check_include_nest_dict,
    generate_nest_field_dict,
)
from fairycloud.utils.fields import reset_field

# 因为每个用户使用的 JSONField 可能是不同的，所以这里
# 需要引用用户使用的 JSONField 字段
JSONField = reset_field.jsonfield()


class ModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        # 获取反向字段 related_name 和 name 的映射
        model = self.Meta.model

        # 获取此模型所有的虚拟关系字段
        virtual_relation_fields = [
            item.name for item in meta.get_virtual_relation_fields(model)
        ]

        # 注意这里的 fields 是 DRF Field 对象列表
        for field in fields:
            if field.field_name in virtual_relation_fields:
                # 注意 django field 和 drf field 的区别
                django_field = meta.get_field(model, field.field_name)
                related_name = meta.get_accessor_name(django_field)

                try:
                    attribute = getattr(instance, related_name)
                    queryset = attribute if django_field.one_to_one else attribute.all()
                    ret[field.field_name] = field.to_representation(queryset)
                except Exception as e:
                    print('errorrrrr', e)
            else:
                try:
                    attribute = field.get_attribute(instance)
                except SkipField:
                    continue

                check_for_none = (
                    attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
                )
                if check_for_none is None:
                    ret[field.field_name] = None
                elif isinstance(attribute, models.Manager):
                    ret[field.field_name] = field.to_representation(attribute.all())
                else:
                    ret[field.field_name] = field.to_representation(attribute)
        return ret


class RecursiveSerializer(serializers.Serializer):
    """递归序列化类，目标是为了形成树形数据结构"""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class DataModelSerializer(ModelSerializer):
    """
    通用的数据类

    由于 BigInteger类型的数据到了前端，JS丢失了精度，所以在接口返回的时候就直接转成字符串
    """

    # 这里使用复制，把  rest_framework 的 serializer_field_mapping 和自定义的 serializer_field_mapping
    # 隔离开
    serializer_field_mapping = copy.deepcopy(ModelSerializer.serializer_field_mapping)
    serializer_field_mapping[models.BigIntegerField] = drf_fields.CharIntegerField
    serializer_field_mapping[models.BigAutoField] = drf_fields.CharIntegerField
    serializer_field_mapping[JSONField] = DrfJsonField


class ExportModelSerializer(ModelSerializer):
    """
    通用的导出类

    因为导出的数据格式和普通的请求返回的数据格式有可能是不一样的，所以重置了 serializer_field_mapping
    """

    # 这里使用复制，把  rest_framework 的 serializer_field_mapping 和自定义的 serializer_field_mapping
    # 隔离开
    serializer_field_mapping = copy.deepcopy(ModelSerializer.serializer_field_mapping)
    serializer_field_mapping[models.BigIntegerField] = drf_fields.CharIntegerField
    serializer_field_mapping[models.BigAutoField] = drf_fields.CharIntegerField
    serializer_field_mapping[JSONField] = DrfJsonField


def create_meta_class(model, display_fields=None, action=None, **kwargs):
    """构建序列化类的 Meta 类"""

    attrs = {'model': model}

    if display_fields:
        fields = display_fields
    else:
        fields = '__all__'

    attrs['fields'] = fields
    return type('Meta', (object,), attrs)


def create_serializer_class(model, action=None, attrs=None, display_fields=None):
    """构建序列化类"""

    if attrs is None:
        attrs = {}

    inherit_class = (
        ExportModelSerializer
        if action == FAIRY_INNER_ACTION_EXPORT_FILE
        else DataModelSerializer
    )

    def __init__(self, *args, **kwargs):
        """
        重置导出的字段映射，因为类似 BooleanField 字段，显示为中文会比较友好
        """
        if action == FAIRY_INNER_ACTION_EXPORT_FILE:
            super(ExportModelSerializer, self).__init__(*args, **kwargs)
        else:
            super(DataModelSerializer, self).__init__(*args, **kwargs)

    # 获取使用 fairyproperty 装饰的字段数据（其实是函数）
    fairy_property_field_dict = get_model_fairy_property_fields(model)
    # FIXME: 只有指定了 display_fields 才会生效
    if fairy_property_field_dict and display_fields:
        for field_name in display_fields:
            if field_name in fairy_property_field_dict:
                property_field = fairy_property_field_dict.get(field_name)
                # 这里指明对应的序列化字段
                attrs[field_name] = get_fairy_property_field_trans_drf_field(
                    property_field.field_type
                )(read_only=True)

    return type(
        f'{model.__name__}ModelSerializer',
        (inherit_class,),
        {
            'Meta': create_meta_class(
                model,
                action=action,
                display_fields=display_fields,
            ),
            'action': action,
            'fairycloud_model': model,
            '__init__': __init__,
            **attrs,
        },
    )


def create_nested_serializer_class(model, field_nest, action=None, **kwargs):
    """构建嵌套序列化类

    此方法仅仅为 create_dynamic_serializer_class 方法服务
    """
    attrs = {}

    for key, value in field_nest.items():
        if not isinstance(value, dict):
            continue

        field = meta.get_field(model, key)
        many = field.many_to_many
        if meta.is_virtual_relation_field(field):
            many = False if field.one_to_one else True

        if check_include_nest_dict(value):
            attrs[key] = create_nested_serializer_class(
                field.related_model,
                value,
                action=action,
            )(many=many)
        else:
            # 这里代表已经是最低级的序列化类，没有嵌套的关系了
            attrs[key] = create_serializer_class(
                field.related_model,
                action=action,
                display_fields=list(value.keys()),
            )(many=many)

    return create_serializer_class(
        model,
        action=action,
        attrs=attrs,
        display_fields=list(field_nest.keys()),
    )


def create_dynamic_serializer_class(model, action=None, display_fields=None):
    """动态创建序列化类"""

    nest_field_dict = {}
    if display_fields:
        nest_field_dict = generate_nest_field_dict(display_fields)

    attrs = {}

    # 处理扩展字段对应的序列化类
    for key, value in nest_field_dict.items():
        if not isinstance(value, dict):
            continue
        field = meta.get_field(model, key)

        # 如果不是关系字段，则略过
        if not meta.is_relation_field(field):
            continue

        # 如果是反向字段，则使用另外一种方式
        many = field.many_to_many
        if meta.is_virtual_relation_field(field):
            # 如果是反向字段，除非是一对一，否则 many 都是 True
            many = False if field.one_to_one else True

        attrs[field.name] = create_nested_serializer_class(
            field.related_model,
            value,
            action=action,
        )(many=many)

    return create_serializer_class(
        model,
        action=action,
        attrs=attrs,
        display_fields=list(nest_field_dict.keys()),
    )
