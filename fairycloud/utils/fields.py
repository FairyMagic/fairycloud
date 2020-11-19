"""
字段处理

因为 fairycloud 业务中使用了一些通用的第三方字段，例如 JSONField，但是
用户每个使用的 JSONField 不是统一，这里是根据用户的配置获取对应的字段，如果用户
没有指定，则使用默认的字段
"""
from django.db import models
from fairycloud.settings import fairycloud_settings


class ResetField:
    """
    重新自定义字段
    """

    def jsonfield(self):
        reset_field = fairycloud_settings.RESET_JSON_FIELD
        if not reset_field:
            # 如果 Django 内置了 JSONField，则优先使用内置字段
            django_jsonfield = getattr(models, 'JSONField', None)
            if django_jsonfield:
                return django_jsonfield
            else:
                # 这里做了额外的动作，不是很漂亮
                from jsonfield import JSONField

                return JSONField
        return reset_field


reset_field = ResetField()
