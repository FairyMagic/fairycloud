from django.conf import settings as django_settings
from django.utils.module_loading import import_string

DEFAULTS = {
    # JSONField 重置，因为用户使用的 JSON 字段类可能是不同的
    "RESET_JSON_FIELD": None,
    # 视图端点配置
    "ENDPOINTS": None,
}

IMPORT_STRINGS = [
    'RESET_JSON_FIELD',
]

REMOVED_SETTINGS = []


def perform_import(val, setting_name):
    """
    引入包
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class FairyCloudSettings:
    """仙女云配置"""

    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)

        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(django_settings, 'FAIRY_CLOUD', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if attr in self.import_strings:
            val = perform_import(val, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(f'{setting} 已经不再使用')
        return user_settings


fairycloud_settings = FairyCloudSettings(None, DEFAULTS, IMPORT_STRINGS)
