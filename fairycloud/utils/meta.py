"""
涉及到 model._meta 相关的工具方法
"""


def get_accessor_name(field):
    """
    反向字段获取 accessor name

    注意：只有反向字段具有这个属性，其他非反向字段不能使用

    TAG: 元工具函数
    """
    return field.get_accessor_name()


def is_relation_field(field):
    """是否是关系字段

    TAG: 元工具函数
    """
    return field.is_relation


def is_concrete_relation_field(field):
    """
    是否是真实的关系字段，即表中真实存在的字段

    TAG: 元工具函数

    class A:
        a = models.ForeignKey()

    那么 A 有一个真实的关系字段 a
    """
    return field.is_relation and field.concrete


def is_virtual_relation_field(field):
    """
    检测字段是否是虚拟关系字段，可以认为是反向字段，但是是虚拟的

    反向字段都是虚拟的

    TAG: 元工具函数

    class A:
        pass

    class B:
        a = field(related_name='b_a')

    那么模型 A 有个虚拟的字段叫做 b_a

    如果没有指定 realated_name，那么这个字段就是 b
    """
    return field.is_relation and not field.concrete


def get_field(model, field_name):
    """
    获取指定名称的字段, 如果是反向关系，则另外处理

    针对下面异常补做情况说明: 即没有指定 related_name 的情况

    class A:
        pass

    class B:
        a = FK(A)

    那么模型 A 有个虚拟的字段叫做 b

    但是前端传入 b_set 时，是找不到对应的字段的，所以这里需要找到反向字段

    通过反向字段计算 accessor_name 进行比对，获取对应的字段
    """
    try:
        return model._meta.get_field(field_name)
    except Exception:
        # 如果找不到，则到反向字段中进行寻找
        for field in get_virtual_relation_fields(model):
            related_name = get_accessor_name(field)
            if related_name == field_name:
                return field


def get_field_by_reverse_field(field):
    """获取字段，通过反转字段

    例如 product 引用了 User，通过 User 的反转字段查找到 product 中对应的字段
    """
    return field.remote_field


def get_related_model_field(model, related_model):
    """
    model 中的关系字段是否指向 related_model

    例如，文章 Article 中的有一个字段

    TODO: 如果单个模型中有两个字段同时引用了同一个模型，这里就会存在问题
    """
    for field in model._meta.get_fields():
        if field.is_relation and field.concrete:
            if field.related_model is related_model:
                return field


def get_concrete_relation_field_by_name(model, field_name):
    """
    通过字段名称获取真实的关系字段
    """
    field = get_field(model, field_name)
    if not field or not is_concrete_relation_field(field):
        return
    return field


def get_virtual_relation_fields(model):
    """
    获取模型所有的反向关系字段
    """
    return [item for item in model._meta.get_fields() if is_virtual_relation_field(item)]


def get_concrete_relation_fields(model):
    """
    获取模型正向所有真实的关系字段
    """
    return [item for item in model._meta.get_fields() if is_concrete_relation_field(item)]


def get_concrete_relation_field(model, field_name):
    """获取模型指定名称的真实的关系字段

    Params:
        model 模型类
        field_name 字段名

    Returns:
        field object 字段对象
    """
    try:
        field = model._meta.get_field(field_name)

        if is_concrete_relation_field(field):
            return field
    except Exception:
        return


def get_concrete_fields(model):
    """
    获取真实存在的字段，包含关系字段和非关系字段
    """
    return [item for item in model._meta.get_fields() if item.concrete]


def get_all_relation_fields(model):
    """
    获取所有的关系字段，包含真实关系字段和虚拟关系字段
    """
    return [item for item in model._meta.get_fields() if is_relation_field(item)]
