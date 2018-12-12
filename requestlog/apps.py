# noinspection PyUnresolvedReferences

from django.apps import AppConfig as BaseAppConfig

class AppConfig(BaseAppConfig):
    name = "requestlog"
    middlewares = (
         (10, 'requestlog.middleware.RequestLoggingMiddleware'),
    )
    def ready(self):
        pass
