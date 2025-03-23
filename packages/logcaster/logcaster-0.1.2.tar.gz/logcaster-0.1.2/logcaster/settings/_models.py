from importlib import import_module
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any


class DiscordEnvironmentVars(BaseSettings):
    webhook_url: str | None = None


class TelegramEnvironmentVars(BaseSettings):
    bot_token: str | None = None
    chat_id: int | None = None


class Environment(BaseSettings):
    discord: DiscordEnvironmentVars | None = None
    telegram: TelegramEnvironmentVars | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_nested_delimiter='__'
    )

    @staticmethod
    def __get_dj_setting(name: str) -> Any | None:
        dj_settings = getattr(import_module('django.conf'), 'settings', None)
        assert dj_settings is not None, 'Logcaster environment vars must be set to any source'        
        return getattr(dj_settings, name, None)

    def model_post_init(self, __context):
        if self.discord or self.telegram:
            print('dc or tg', self.discord, self.telegram)
            return True
        
        LOGCASTER_TELEGRAM_BOT_TOKEN = self.__get_dj_setting('LOGCASTER_TELEGRAM_BOT_TOKEN')
        LOGCASTER_TELEGRAM_CHAT_ID = self.__get_dj_setting('LOGCASTER_TELEGRAM_CHAT_ID')
        
        LOGCASTER_DISCORD_WEBHOOK_URL = self.__get_dj_setting('LOGCASTER_DISCORD_WEBHOOK_URL')
        
        is_using_telegram = LOGCASTER_TELEGRAM_BOT_TOKEN or LOGCASTER_TELEGRAM_CHAT_ID
        if is_using_telegram:
            assert LOGCASTER_TELEGRAM_BOT_TOKEN and LOGCASTER_TELEGRAM_CHAT_ID, (
                'telegram must have both `LOGCASTER_TELEGRAM_BOT_TOKEN` '
                'and `LOGCASTER_TELEGRAM_CHAT_ID` provided'
            )
            self.telegram = TelegramEnvironmentVars(
                bot_token=LOGCASTER_TELEGRAM_BOT_TOKEN,
                chat_id=LOGCASTER_TELEGRAM_CHAT_ID,
            )
        
        if LOGCASTER_DISCORD_WEBHOOK_URL:
            self.discord = DiscordEnvironmentVars(
                webhook_url=LOGCASTER_DISCORD_WEBHOOK_URL
            )
        
        assert self.telegram or self.discord, 'A Logcaster source must be configured'

        return True


__all__ = ['Environment']
