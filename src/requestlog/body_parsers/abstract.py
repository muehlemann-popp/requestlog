import abc

from django.core.handlers.wsgi import WSGIRequest


class AbstractBodyParser(abc.ABC):
    """Class for the body request parsing"""

    @abc.abstractmethod
    def parse(self, request: WSGIRequest) -> dict:
        """Parse request body"""
