from ya_oauth import YandexOAuth

PROVIDERS = {
    'yandex': YandexOAuth()
}


class OAuthService:
    def __init__(self, provider_name: str):
        self.oauth_provider = PROVIDERS.get(provider_name)
        if not self.oauth_provider:
            raise ValueError(f"Unsupported provider: {provider_name}")

    async def get_user_info(self, token: str) -> dict:
        return await self.oauth_provider.get_user_info(token)
