import requests
from core.config import settings


def get_oauth_url(provider_name: str) -> str:
    if provider_name == settings.authorize_provider:
        return (
            f"{settings.authorize_url}?"
            f"response_type=code&client_id={settings.client_id}&"
            f"redirect_uri={settings.redirect_uri}"
        )
    raise ValueError(f"Unsupported provider: {provider_name}")


async def get_token(provider_name: str, code: str) -> str:
    if provider_name == settings.authorize_provider:
        url = settings.access_token_url
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "redirect_uri": settings.redirect_uri,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get('access_token')
        except requests.RequestException as e:
            print(f"Error obtaining {provider_name} token: {e}")
            return None
    raise ValueError(f"Unsupported provider: {provider_name}")