from django.utils.encoding import force_text

PARAMETER_FORMAT_ERROR = 10000
PARAMETER_BUSINESS_ERROR = 10001
SERVER_IS_BUSY = 10002
REQUEST_FORBIDDEN = 10003
OBJECT_NOT_FOUND = 10004
APP_LABEL_IS_INVALID = 10005
MODEL_SLUG_IS_INVALID = 10006
CANT_NOT_FIND_MODEL = 10007
BATCH_ACTION_HAND_ERROR = 10008
FUNCTION_NOT_FOUNT = 10009


ERROR_PHRASES = {
    PARAMETER_FORMAT_ERROR: '参数格式错误',
    PARAMETER_BUSINESS_ERROR: '参数业务错误',
    SERVER_IS_BUSY: '服务器繁忙，请稍后再试',
    REQUEST_FORBIDDEN: '您没有执行该操作的权限',
    OBJECT_NOT_FOUND: '找不到对应的数据',
    APP_LABEL_IS_INVALID: '路由中指定的应用标识不合法',
    MODEL_SLUG_IS_INVALID: '路由中指定的模型标识不合法',
    CANT_NOT_FIND_MODEL: '找不到指定的模型',
    BATCH_ACTION_HAND_ERROR: '批量操作执行异常',
    FUNCTION_NOT_FOUNT: '找不到对应的函数处理器',
}


class FairyCloudException(Exception):
    """通用业务异常类"""

    # 默认的错误码
    default_error_code = 9000

    # 友好可读的异常报错信息
    default_error_message = '系统错误'

    # 对程序员友好的详尽的异常报错数据
    default_error_data = ''

    # 异常出错的应用标识
    default_error_app = 'fairycloud'

    def __init__(
        self, error_code=None, error_message=None, error_data=None, error_app=None
    ):

        self.error_code = (
            error_code if error_code is not None else self.default_error_code
        )

        if error_message is not None:
            self.error_message = error_message
        else:
            get_message = ''
            if error_code in ERROR_PHRASES:
                get_message = force_text(ERROR_PHRASES.get(error_code))
            if not get_message:
                get_message = force_text(self.default_error_message)
            self.error_message = get_message

        self.error_data = error_data if error_data else self.default_error_data
        self.error_app = error_app if error_app else force_text(self.default_error_app)

    def __str__(self):
        return (
            f'{self.error_code}-{self.error_app}:{self.error_message},{self.error_data}'
        )
