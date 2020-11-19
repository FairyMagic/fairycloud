"""
创建，更新操作时，客户端一般情况下，可以不用传入当前登录用户的字段数据
通过对应的配置自动插入用户字段数据，当然用户可以根据对应的配置，针对
指定的方法决定是否开启使用此功能

注意：
- 此业务处理使用白名单方式，只有明确配置开启，才会处理
- 业务处理只处理一层数据，不会对数据进行嵌套递归处理
"""
from django.contrib.auth import get_user_model

from fairycloud.const import FAIRY_STATEMENT_USER_PIP_CONFIG
from fairycloud.utils.meta import get_related_model_field

# 对应视图处理函数的集合
VALID_ACTION_SET = {'create', 'update', 'partial_update', 'patch_enhance'}


def fairy_pip_user_add_handle(view, data):
    """
    用户数据处理管道

    Params:
        view object 视图对象
        data dict 字典
    """

    # 当前只有创建和更新支持用户数据处理并且是已经通过认证的用户
    if view.action.lower() not in VALID_ACTION_SET or view.request.user.is_anonymous:
        return

    # 这里注意个细节，data 可能是空数据，如果是空数据，这种场景也没有什么意义
    # 这意味着模型可能包含两个字段，一个主键和一个用户字段，目前不知道注意的场景
    # 有什么意义
    if not data or not isinstance(data, dict):
        return

    # 查看配置，用户是否已经配置对应的 action 是否可以处理
    config = getattr(
        view.fairy_instance.statements_class, FAIRY_STATEMENT_USER_PIP_CONFIG, None
    )
    # 如果配置为空，则不进行任何处理
    if not config or not isinstance(config, dict):
        return

    # 检查配置的数据是否合法
    field_name, action_enabled = config.get('field'), config.get('action_enabled')
    if (
        not field_name
        or not isinstance(field_name, str)
        or not action_enabled
        or not isinstance(action_enabled, dict)
        or not action_enabled.get(view.action)
    ):
        return

    # 根据字段检查是否可以找到对应的用户字段数据
    USER_MODEL = get_user_model()
    user_relation_field = get_related_model_field(view.fairy_instance.model, USER_MODEL)
    if not user_relation_field:
        return

    if field_name not in data:
        data[field_name] = view.request.user.id
    return data
