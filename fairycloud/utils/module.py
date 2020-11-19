from importlib import import_module
from importlib.util import find_spec

# 放全局的文件夹名称
FAIRYCLOUD_GLOBAL_MODULE = 'fairyglobalspace'

# 单一具体应用下局部文件夹名称
FAIRYCLOUD_SPACE_NAME = 'fairyspace'

# 处理的视图
FAIRYCLOUD_VIEWS = 'views'

# 声明配置类
FAIRYCLOUD_STATEMENTS = 'statements'

# 自定义校验表单
FAIRYCLOUD_FORM = 'forms'

# 管理后台自定义的导出序列化类
FAIRYCLOUD_EXPORT = 'exports'


def fairy_load_app_module(app_label, module_slug=None):
    """加载指定的模块"""
    if not module_slug:
        return
    try:
        module_name = f'{app_label}.{FAIRYCLOUD_SPACE_NAME}.{module_slug}'
        module = find_spec(module_name)
        if module:
            return import_module(module_name)
    except ModuleNotFoundError:
        return


def fairy_load_global_module(app_label, module_slug=None):
    """加载全局的模块"""
    try:
        module_name = f'{FAIRYCLOUD_GLOBAL_MODULE}.{app_label}.{module_slug}'
        module = find_spec(module_name)
        if module:
            return import_module(module_name)
    except ModuleNotFoundError:
        return


def fairy_load_module(app_label, module_slug):
    """加载全局空间对应的模块和应用空间对应的模块"""
    global_module = fairy_load_global_module(app_label, module_slug)
    app_module = fairy_load_app_module(app_label, module_slug)
    return global_module, app_module


def fairy_load_views(app_label):
    """加载视图"""
    return fairy_load_module(app_label, FAIRYCLOUD_VIEWS)


def fairy_load_statements(app_label):
    """加载配置声明模块"""
    return fairy_load_module(app_label, FAIRYCLOUD_STATEMENTS)


def fairy_load_forms(app_label):
    """加载认证表单模块"""
    return fairy_load_module(app_label, FAIRYCLOUD_FORM)


def import_class_from_string(dotted_path):
    """
    尝试从一个字符串中加载一个类
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        raise ImportError(f"{dotted_path} 不是一个模块路径")

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError(f'模块 {module_path} 没有定义一个 {class_name} 属性/类')
