import copy
from django.urls import path, include
from fairycloud.drfbox.routers import FairyCloudSimpleRouter
from fairycloud.settings import fairycloud_settings
from fairycloud.utils.module import import_class_from_string


def make_urls_class(endpoint, attrs):
    """
    根据指定的 endpoint 和端点对应的配置，动态构建视图，然后自动注册

    Params:
        endpoint str 例如 client, manage
        attrs dict | None 端点对应的配置
    """
    from fairycloud.restful.viewsets import FairyModelViewSet

    new_attrs = copy.deepcopy(attrs) if attrs and isinstance(attrs, dict) else {}
    # 默认视图的端点是有 endpoint 来指定
    new_attrs['end_slug'] = endpoint

    # 视图类
    view_class = None

    # 检测是否在配置中定义了对应的视图类
    if 'views' in new_attrs and new_attrs.get('views'):
        try:
            view_class = import_class_from_string(new_attrs['views'])
        except Exception:
            pass

    # 如果配置中找不到对应的视图类，则默认新建对应的视图类
    if not view_class:
        view_class = type(endpoint.title(), (FairyModelViewSet,), new_attrs)

    router = FairyCloudSimpleRouter(custom_base_name=f'fairycloud-{endpoint}')
    router.register('', view_class)
    return router.urls


def get_fairycloud_urls():
    """动态根据配置生成对应的路由"""

    urlpatterns = []
    end_points = fairycloud_settings.ENDPOINTS
    if not end_points or not isinstance(end_points, dict):
        raise Exception('路由 endpoints 配置应该是一个字典')

    for key, value in end_points.items():
        urlpatterns.append(
            path(
                f'fairycloud/{key}/<str:app>/<str:model>/',
                include(make_urls_class(key, value)),
            )
        )
    return urlpatterns


urlpatterns = get_fairycloud_urls()
