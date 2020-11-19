from fairycloud.restful.forms import get_form_class


class FormMixin:
    """数据验证表单"""

    def get_validate_form(self, action):
        """获取数据校验表单"""
        return get_form_class(self, action)
