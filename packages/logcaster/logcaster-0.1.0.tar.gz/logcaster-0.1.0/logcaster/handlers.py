import json
import logging
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from discord_webhook import DiscordEmbed, DiscordWebhook

from .settings import ENV


class BaseHandler(logging.Handler):
    def __init__(self, level = logging.ERROR):
        super().__init__(level)


class DiscordHandler(BaseHandler):
    def get_webhook(self) -> DiscordWebhook:
        return DiscordWebhook(ENV.discord.webhook_url)
    
    def emit(self, record: logging.LogRecord) -> None:
        webhook = self.get_webhook()

        fmt = self.format(record)
        if isinstance(fmt, DiscordEmbed):
            webhook.add_embed(fmt)
        else:
            webhook.content = fmt
        
        try:
            webhook.execute()
            sys.stdout.write('logger sent to discord\n')
        
        except Exception as e:
            sys.stderr.write('fail to sending logging to Discord: %s\n' % str(e))
            sys.stderr.write(f'lost message: {record.getMessage()}')


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


__all__ = ["DiscordHandler", "TelegramHandler"]
