import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from tabulate import tabulate

from .formatters import BaseFormatter
from .handlers import BaseHandler
from .settings import ENV


class TelegramFormatter(BaseFormatter):
    def __init__(self, include_fields=None, exclude_fields=None):
        super().__init__()
        self.include_fields = include_fields or []
        self.exclude_fields = exclude_fields or []

    def format(self, record):
        data = self._get_fields(record)
        table = tabulate(data.items(), tablefmt='presto', headers=['field', 'value'])
        return table


class TelegramHandler(BaseHandler):
    def emit(self, record):
        out = self.format(record)
        out = f"```\n{out}\n```"
        chat_id = ENV.telegram.chat_id
        data = json.dumps(
            {"text": out, "chat_id": chat_id, "parse_mode": "MarkdownV2"}
        ).encode("utf-8")

        request = Request(
            f"https://api.telegram.org/bot{ENV.telegram.bot_token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            urlopen(request)
            sys.stdout.write(f"Logging sent to telegram chat id {chat_id}\n")

        except HTTPError as e:
            sys.stdout.write(f"error when logging to telegram: {e.read().decode()}\n")
            return False

        except Exception as e:
            sys.stderr.write(f"error when logging to telegram: {str(e)}\n")
            sys.stderr.write(out + "\n")
            return False

        return True


__all__ = ['TelegramHandler', 'TelegramFormatter']