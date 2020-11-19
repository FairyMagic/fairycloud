import inspect
from rest_framework import viewsets

from fairycloud.drfbox.pagination import PageNumberPagination

from fairycloud.restful.instancespace import FairyInstance

from fairycloud.restful.mixins import views
from fairycloud.restful.mixins.fairy import FairyCloudMixin
from fairycloud.restful.mixins.forms import FormMixin

from fairycloud.restful.serializers import create_dynamic_serializer_class
from fairycloud.utils import module


class FairyGenericViewSet(
    FairyCloudMixin,
    FormMixin,
    viewsets.GenericViewSet,
):

    pagination_class = PageNumberPagination

    def _get_user_custom_config_classes(self, classes_name):
        """
        根据级别，依次获取
        - 方法级别的配置类: 查找自定义的方法是否存在对应的属性
        - 对应自定义视图的配置类：用户定义的视图是否存在对应的属性
        - 顶级入口视图的配置类：顶级视图是否存在对应的属性
        """
        classes = None
        if self.fairy_instance.custom_action_handler:
            classes = getattr(
                self.fairy_instance.custom_action_handler, classes_name, None
            )
        if classes is None and self.fairy_instance.custom_view_instance:
            classes = getattr(
                self.fairy_instance.custom_view_instance, classes_name, None
            )
        if classes is None:
            classes = getattr(self, classes_name, None)
        return classes

    def _get_class_instances(self, classes_name):

        class_lists = self._get_user_custom_config_classes(classes_name)

        instance_list = []
        for item in class_lists:
            if inspect.isclass(item):
                instance_list.append(item())
            elif isinstance(item, str):
                try:
                    perm_class = module.import_class_from_string(item)
                    instance_list.append(perm_class())
                except Exception:
                    pass
        return instance_list

    def get_renderers(self):
        return self._get_class_instances('renderer_classes')

    def get_parsers(self):
        return self._get_class_instances('parser_classes')

    def get_authenticators(self):
        return self._get_class_instances('authentication_classes')

    def get_permissions(self):
        return self._get_class_instances('permission_classes')

    def get_throttles(self):
        return self._get_class_instances('throttle_classes')

    def initialize_request(self, request, *args, **kwargs):
        FairyInstance.set_namespace_instance(self)
        return super().initialize_request(request, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        """
        添加额外的检测和声明处理
        """

        # 获取请求端的命名空间
        self.fairy_get_request_namespace(request, *args, **kwargs)

        # 处理模型
        self.fairy_get_model(request, *args, **kwargs)

        # 合并用户定义的顶级空间和应用空间下的视图，动态构建新视图
        # 并实例化新视图，进行缓存，后续如果需要获取具体 action 的
        # 权限类和其他类，都会通过此实例对象进行处理
        self.fairy_get_custom_view_instance()

        # 结合上一步，获取对应的自定义动作处理器
        self.fairy_custom_action_handler()

        result = super().initial(request, *args, **kwargs)

        # 获取配置声明
        self.fairy_get_statements()
        # 处理扩展字段
        self.fairy_get_expand_fields(request, *args, **kwargs)

        return result

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        result = super().get_serializer_context()
        result['user'] = self.request.user
        return result

    def get_queryset(self):
        """动态的计算结果集

        处理扩展字段，然后 prefetch_related

        - 如果是展开字段，这里做好是否关联查询
        """
        queryset = self.fairy_instance.model.objects.all()
        transform_expand_fields = self.fairy_instance.transform_expand_fields

        if transform_expand_fields:
            # 把处理后的扩展字段替换 __ 然后进行 prefetch_related 操作
            field_list = [item.replace('.', '__') for item in transform_expand_fields]
            queryset = queryset.prefetch_related(*field_list)
        return queryset

    def get_serializer_class(self):
        """动态的获取序列化类"""
        return create_dynamic_serializer_class(
            model=self.fairy_instance.model,
            action=self.action,
            display_fields=self.fairy_instance.display_fields,
        )


class FairyReadOnlyModelViewSet(
    views.FairyRetrieveModelMixin,
    views.FairyPostRetrieveModelMixin,
    views.FairyListModelMixin,
    views.FairyPostListModelMixin,
    FairyGenericViewSet,
):
    """
    只拥有只读属性的基类
    """

    pass


class FairyModelViewSet(
    views.FairyRetrieveModelMixin,
    views.FairyPostRetrieveModelMixin,
    views.FairyDestroyModelMixin,
    views.FairyListModelMixin,
    views.FairyPostListModelMixin,
    views.FairyCreateModelMixin,
    views.FairyUpdateModelMixin,
    views.FairyPutPartialUpdateModelMixin,
    views.FairyCloudFuncMixin,
    views.FairyBatchProcessMixin,
    FairyGenericViewSet,
):
    """
    所有端共用的基类
    """

    pass
