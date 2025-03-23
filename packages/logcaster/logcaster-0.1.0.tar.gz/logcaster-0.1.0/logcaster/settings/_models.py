from pydantic_settings import BaseSettings, SettingsConfigDict


class DiscordEnvironmentVars(BaseSettings):
    api_token: str | None = None
    app_id: int | None = None
    client_secret: str | None = None
    public_key: str | None = None
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

    @property
    def check(self) -> bool:
        if not (self.discord or self.telegram):
            raise RuntimeError('DISCORD or TELEGRAM environment vars must be set')
        return True


__all__ = ['Environment']
