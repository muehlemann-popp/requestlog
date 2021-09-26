# noinspection PyUnresolvedReferences

from django.apps import AppConfig as BaseAppConfig
import django

class AppConfig(BaseAppConfig):
    name = "requestlog"
    middlewares = (
         (10, 'requestlog.middleware.RequestLoggingMiddleware'),
    )
    default_auto_field = 'django.db.models.AutoField'
