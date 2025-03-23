import logging
from tabulate import tabulate
from discord_webhook import DiscordEmbed


class BaseFormatter(logging.Formatter):
    def __init__(self, include_fields: list[str] = None, exclude_fields: list[str] = None, *args, **kwargs):
        assert not (include_fields and exclude_fields), "`include_fields` and `exclude_fields` are exclusionary"

        super().__init__(*args, **kwargs)
        self.include_fields = include_fields or ['__all__']
        self.exclude_fields = exclude_fields or []
        

    def _get_fields(self, record: logging.LogRecord) -> dict:
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        record_dict = record.__dict__

        if self.include_fields == ['__all__']:
            self.include_fields = [k for k in record.__dict__.keys() if k not in self.exclude_fields]
        
        elif self.include_fields:
            return {key: value for key, value in record_dict.items() if key in self.include_fields}
        
        return {key: value for key, value in record_dict.items() if key not in self.exclude_fields}


class DiscordFormatter(BaseFormatter):
    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', 'EasyLog')
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


class TelegramFormatter(BaseFormatter):
    def __init__(self, include_fields=None, exclude_fields=None):
        super().__init__()
        self.include_fields = include_fields or []
        self.exclude_fields = exclude_fields or []

    def format(self, record):
        data = self._get_fields(record)
        table = tabulate(data.items(), tablefmt='presto', headers=['field', 'value'])
        return table


__all__ = ['DiscordFormatter', 'TelegramFormatter']
