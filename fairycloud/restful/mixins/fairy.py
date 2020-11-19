from django.apps import apps

from fairycloud import const
from fairycloud.utils import meta, data
from fairycloud.utils.module import fairy_load_statements, fairy_load_views


class FairyCloudMixin:
    """添加的自定义业务处理"""

    def fairy_rewrite_permission_class(self):
        """重置"""
        pass

    def fairy_get_statements(self):
        """获取配置声明类"""

        def get_statements(view_module):
            if not view_module:
                return

            model_title = self.fairy_instance.model.__name__
            class_name = f'{model_title}{self.end_slug.title()}Statements'
            return getattr(view_module, class_name, None)

        statements_class = None
        global_statements, app_statements = fairy_load_statements(
            self.fairy_instance.app_label
        )

        class_list = [get_statements(global_statements), get_statements(app_statements)]
        class_list = tuple((item for item in class_list if item))
        if class_list:
            statements_class = type('StatementsConfig', class_list, {})
        self.fairy_instance.statements_class = statements_class

    def fairy_get_custom_view_instance(self):
        """
        获取用户自定义的顶级命名空间的视图对象和应用空间下的视图对象

        即自定义在 views.py 中，

        格式为 '{model_title}{self.end_slug.title()}ViewSets'

        的对象
        """

        def get_view_class(view_module):
            if not view_module:
                return

            model_title = self.fairy_instance.model.__name__
            view_class_name = f'{model_title}{self.end_slug.title()}ViewSets'
            return getattr(view_module, view_class_name, None)

        # 先查询对应的全局视图
        top_module, app_module = fairy_load_views(self.fairy_instance.app_label)
        class_list = [get_view_class(top_module), get_view_class(app_module)]
        class_list = tuple((item for item in class_list if item))

        if class_list:
            custom_views = type('CustomViewSets', class_list, {})
            self.fairy_instance.custom_view_instance = custom_views()

    def fairy_custom_action_handler(self):
        """
        从模块中找对应的处理器，这里的处理器都是对应每个 action，用户
        可以在全局空间和应用空间下重写对应的 action（例如 list，retrieve 等等)

        获取到对应请求接收处理器后，后续针对权限，认证，限流等等类的处理，划分为三个级别

        - 具体方法级别的配置类（权限，认证等等）
        - 具体应用自定义视图指定的配置类
        - 最顶级基础入口级别的配置类
        """
        custom_view_instance = self.fairy_instance.custom_view_instance

        if custom_view_instance:
            action_name = self.action

            if self.action == 'cloudfunc':
                cloudfunc_name = self.fairy_instance.request_namespace.get(
                    const.FAIRY_CALLED_FUNC_NAME
                )
                action_name = f'cloudfunc_{cloudfunc_name}'
            elif self.action == 'batch':
                batchfunc_name = self.fairy_instance.request_namespace.get(
                    const.FAIRY_CALLED_FUNC_NAME
                )
                action_name = f'batch_{batchfunc_name}'

            self.fairy_instance.custom_action_handler = getattr(
                custom_view_instance, action_name, None
            )

    def fairy_get_request_namespace(self, request, *args, **kwargs):
        """获取请求端命名空间对应的参数

        请求端传入的格式：
        {
            fairycloud: {
                expand_fields: [],
                display_fields: [],
                ....
            },
            data: 数据
        }
        """
        self.fairy_instance.request_namespace = request.data.get(
            const.FAIRY_CALLED_NAMESPACE, {}
        )
        if not isinstance(self.fairy_instance.request_namespace, dict):
            self.fairy_instance.request_namespace = {}

    def fairy_get_model(self, request, *args, **kwargs):
        """
        获取模型
        """
        self.fairy_instance.app_label = self.kwargs.get('app')
        self.fairy_instance.model_label = self.kwargs.get('model')
        self.fairy_instance.model = apps.get_model(
            self.fairy_instance.app_label, self.fairy_instance.model_label
        )

    def fairy_get_expand_fields(self, request, *args, **kwargs):
        """获取扩展字段

        这里通过客户端传递过来的 display_fields 进行扩展字段的筛选和处理
        """
        try:
            self.fairy_instance.display_fields = (
                self.fairy_instance.request_namespace.get(
                    const.FAIRY_CALLED_DISPLAY_FIELDS
                )
            )
            self.fairy_instance.expand_fields = data.get_prefetch_fields(
                self.fairy_instance.display_fields
            )

            self.fairy_translate_expand_fields(self.fairy_instance.expand_fields)
        except Exception:
            pass

    def fairy_translate_expand_fields(self, expand_fields):
        """转换展开字段

        例如

        article.tag.user 会转换成 article.tag_set.user

        即 article.tag.user 中包含虚拟关系字段，则会转换为虚拟关系字段的 accessor name

        这里做转换，是为了后续做 prefetch_related
        """
        if not self.fairy_instance.expand_fields:
            return

        if self.fairy_instance.transform_expand_fields:
            return

        result = []
        for _, item in enumerate(expand_fields):
            field_list, model = item.split('.'), self.fairy_instance.model

            for index, value in enumerate(field_list):
                field = model._meta.get_field(value)

                # 这里只有是关系字段才会处理，如果不是，则直接忽略
                if not meta.is_relation_field(field):
                    continue

                # 虚拟的关系字段
                if meta.is_virtual_relation_field(field):
                    # 如果是虚拟的关系字段，则使用祖宗名称，因为只有祖宗名称才能 prefetch_related
                    accessor_name = meta.get_accessor_name(field)
                    if accessor_name:
                        field_list[index] = accessor_name

                model = field.related_model
            result.append('.'.join(field_list))
        self.fairy_instance.transform_expand_fields = result
