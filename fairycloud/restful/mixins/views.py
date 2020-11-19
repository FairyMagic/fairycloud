from django.db import transaction
from rest_framework.decorators import action

from fairycloud.const import FAIRY_CALLED_FUNC_NAME
from fairycloud.core import exceptions
from fairycloud.drfbox.response import success_response

from fairycloud.restful.batch_process import BatchProcessForm
from fairycloud.restful.userpips import fairy_pip_user_add_handle


class FairyRetrieveModelMixin:
    """检索单个对象"""

    def fairy_connate_retrieve(self, request, *args, **kwargs):
        """原生的检索"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        获取数据详情
        """
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)

        return self.fairy_connate_retrieve(request, *args, **kwargs)


class FairyPostRetrieveModelMixin:
    """post 型的检索数据"""

    def fairy_connate_retrieve_enhance(self, request, *args, **kwargs):
        """原生的检索"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='retrieve')
    def retrieve_enhance(self, request, *args, **kwargs):
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)

        return self.fairy_connate_retrieve_enhance(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='retrieve/mine')
    def retrieve_mine(self, request, *args, **kwargs):
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)

        return self.fairy_connate_retrieve_enhance(request, *args, **kwargs)


class FairyDestroyModelMixin:
    """
    删除一条指定的对象
    """

    def perform_destroy(self, instance):
        instance.delete()

    def fairy_connate_destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response()

    def destroy(self, request, *args, **kwargs):
        """
        删除数据
        """
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_destroy(request, *args, **kwargs)


class _BaseListModel:
    """列表查询基类"""

    def _list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return success_response(response.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)


class FairyListModelMixin(_BaseListModel):
    """获取列表数据"""

    def fairy_connate_list(self, request, *args, **kwargs):
        return self._list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_list(request, *args, **kwargs)


class FairyPostListModelMixin(_BaseListModel):
    """POST 型获取列表"""

    def fairy_connate_list_enhance(self, request, *args, **kwargs):
        return self._list(request, *args, **kwargs)

    @action(methods=['POST'], detail=False, url_path='list')
    def list_enhance(self, request, *args, **kwargs):
        """
        增强型的获取列表数据

        请求方法为：POST
        """
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_list_enhance(request, *args, **kwargs)

    @action(methods=['POST'], detail=False, url_path='list/mine')
    def list_mine(self, request, *args, **kwargs):
        """
        增强型的专属针对当前登录用户获取列表数据

        请求方法为：POST
        """
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_list_enhance(request, *args, **kwargs)


class FairyCreateModelMixin:
    """客户端的创建类"""

    def perform_create(self, serializer):
        return serializer.save()

    def fairy_connate_create(self, request, *args, **kwargs):
        data = request.data.get('data', {})
        with transaction.atomic():
            # 处理正向的关系数据
            fairy_pip_user_add_handle(self, data)
            serializer = self.get_validate_form(self.action)(data=data)
            serializer.is_valid(raise_exception=True)

            instance = self.perform_create(serializer)
            serializer = self.get_serializer(instance)
            return success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_create(request, *args, **kwargs)


class _BaseUpdateModel:
    """更新动作基类"""

    def perform_update(self, serializer):
        return serializer.save()

    def _update(self, request, partial, *args, **kwargs):
        data = request.data.get('data', {})
        instance = self.get_object()

        with transaction.atomic():
            fairy_pip_user_add_handle(self, data)
            serializer = self.get_validate_form(self.action)(
                instance, data=data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            instance = self.perform_update(serializer)
            serializer = self.get_serializer(instance)
            return success_response(serializer.data)


class FairyUpdateModelMixin(_BaseUpdateModel):
    """更新数据"""

    def fairy_connate_update(self, request, *args, **kwargs):
        return self._update(request, False, *args, **kwargs)

    def fairy_connate_partial_update(self, request, *args, **kwargs):
        return self._update(request, True, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """全量更新数据"""
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """部分字段更新"""
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_partial_update(request, *args, **kwargs)


class FairyPutPartialUpdateModelMixin(_BaseUpdateModel):
    """put 型的部分更新

    因为有些端不支持或者不推荐使用 patch 方法
    """

    def fairy_connate_patch_enhance(self, request, *args, **kwargs):
        return self._update(request, True, *args, **kwargs)

    @action(methods=['put'], detail=True, url_path='patch')
    def patch_enhance(self, request, *args, **kwargs):
        reset_handler = self.fairy_instance.custom_action_handler
        if reset_handler:
            return reset_handler(self, request, *args, **kwargs)
        return self.fairy_connate_patch_enhance(request, *args, **kwargs)


class FairyCloudFuncMixin:
    """云函数"""

    @action(methods=['post'], detail=False, url_path='cloudfunc')
    def cloudfunc(self, request, *args, **kwargs):
        data = request.data.get('data')
        func_name = self.fairy_instance.request_namespace.get(FAIRY_CALLED_FUNC_NAME)
        handler = self.fairy_instance.custom_action_handler

        if not handler:
            raise exceptions.FairyCloudException(
                error_code=exceptions.FUNCTION_NOT_FOUNT,
                error_data=f'找不到对应的云函数处理器: {func_name}',
            )

        result = handler(self, request, data, *args, **kwargs)
        return success_response(result)


class FairyBatchProcessMixin:
    """批量处理"""

    @action(methods=['post'], detail=False, url_path='batch')
    def batch(self, request, *args, **kwargs):
        """
        批量处理
        """
        data = {
            'data': request.data.get('data'),
            'func_name': self.fairy_instance.request_namespace.get(
                FAIRY_CALLED_FUNC_NAME
            ),
        }

        serializer = BatchProcessForm(data=data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        response = serializer.handle(self, request, *args, **kwargs)
        return success_response(response)
