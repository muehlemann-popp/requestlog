from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

from requestlog.body_parsers.abstract import AbstractBodyParser  # noqa: F401


def get_body_parser_class(import_path=None):
    return import_string(import_path or settings.REQUEST_LOGGING_BODY_PARSER)


class DefaultBodyParser(LazyObject):
    """Allows to lazy load body parser

    Note:
        - it must be inherited from AbstractBodyParser
    """
    def _setup(self):
        self._wrapped = get_body_parser_class()()


default_body_parser = DefaultBodyParser()
