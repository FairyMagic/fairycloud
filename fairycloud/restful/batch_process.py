from rest_framework import serializers
from fairycloud.core import exceptions


class BatchProcessForm(serializers.Serializer):
    """批量处理的检测表单"""

    func_name = serializers.CharField(max_length=50)
    data = serializers.ListField(min_length=1)

    def validate_func_name(self, value):
        view = self.context['view']
        self.batch_action = view.fairy_instance.custom_action_handler

        if not self.batch_action:
            raise exceptions.FairyCloudException(
                error_code=exceptions.PARAMETER_FORMAT_ERROR,
                error_data='传入的 action: {} 不支持'.format(value),
            )
        return value

    def validate_data(self, value):
        model = self.context.get('view').fairy_instance.model
        filter_params = {f'{model._meta.pk.name}__in': value}

        queryset = model.objects.filter(**filter_params)
        if len(value) != queryset.count():
            raise exceptions.FairyCloudException(
                error_code=exceptions.PARAMETER_BUSINESS_ERROR,
                error_message='列表中包含不合法 id 的数据',
            )
        self.batch_queryset = queryset
        return value

    def handle(self, view, request, *args, **kwargs):
        try:
            return self.batch_action(view, request, self.batch_queryset, *args, **kwargs)
        except Exception as e:
            raise exceptions.FairyCloudException(
                error_code=exceptions.BATCH_ACTION_HAND_ERROR, error_data=str(e)
            )
