import logging


class BaseHandler(logging.Handler):
    def __init__(self, level = logging.ERROR):
        super().__init__(level)


__all__ = ["BaseHandler"]
