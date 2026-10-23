# noinspection PyUnresolvedReferences

from django.apps import AppConfig as BaseAppConfig
from django.core import checks
import django

class AppConfig(BaseAppConfig):
    name = "requestlog"
    middlewares = (
         (10, 'requestlog.middleware.RequestLoggingMiddleware'),
    )
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from .checks import check_settings
        checks.register(check_settings)
