import logging
import sys

from discord_webhook import DiscordEmbed, DiscordWebhook

from .formatters import BaseFormatter
from .handlers import BaseHandler
from .settings import ENV


class DiscordFormatter(BaseFormatter):
    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', 'Logcaster')
        self.thumbnail = kwargs.pop('thumbnail_url', None)
        self.image = kwargs.pop('image_url', None)

        super().__init__(*args, **kwargs)

        self.COLORS = {
            logging.DEBUG: "3498db",  # blue
            logging.INFO: "2ecc71",  # green
            logging.WARNING: "f1c40f",  # yellow
            logging.ERROR: "e74c3c",  # red
            logging.CRITICAL: "8e44ad",  # purple
        }
                
        self.EMOJIS = {
            logging.DEBUG: "\U0001f41b",  # 🐛
            logging.INFO: "\U0001f4ac",  # 💬
            logging.WARNING: "\U000026a0",  # ⚠️
            logging.ERROR: "\U00002757",  # ❗
            logging.CRITICAL: "\U0001f4a5",  # 💥
        }

        self.RESET = "\033[0m"

    def _get_emoji(self, record):
        return self.EMOJIS.get(record.levelno, "")

    def _get_level_name_with_emoji(self, record):
        emoji = self._get_emoji(record)
        levelname = f"{emoji} {record.levelname} {emoji}"
        return levelname
    
    def _get_color(self, record: logging.LogRecord) -> str:
        """return the hex color by the record.levelno attribute"""
        return self.COLORS.get(record.levelno, logging.INFO)

    def format(self, record: logging.LogRecord) -> DiscordEmbed:
        embed = DiscordEmbed(
            title=self._get_level_name_with_emoji(record),
            description=record.getMessage(),
            color=self._get_color(record),
        )

        self.thumbnail and embed.set_thumbnail(self.thumbnail)
        self.image and embed.set_image(self.image)

        embed.set_author(name=self.author)

        embed.set_footer(text="powered by @Low")
        embed.set_timestamp()

        data = self._get_fields(record)
        [embed.add_embed_field(name=field, value=str(value)) for field, value in data.items()]
        return embed


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


__all__ = ['DiscordHandler', 'DiscordFormatter']
