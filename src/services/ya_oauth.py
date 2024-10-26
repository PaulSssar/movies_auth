import requests
from core.config import settings


def get_yandex_oauth_url() -> str:
    return (
        f"https://oauth.yandex.ru/authorize?"
        f"response_type=code&client_id={settings.yandex_client_id}&"
        f"redirect_uri={settings.yandex_redirect_uri}"
    )


async def get_yandex_token(code: str) -> str:
    url = "https://oauth.yandex.ru/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.yandex_client_id,
        "client_secret": settings.yandex_client_secret,
        "redirect_uri": settings.yandex_redirect_uri,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get('access_token')
    except requests.RequestException as e:
        print(f"Error obtaining Yandex token: {e}")
        return None


async def get_yandex_user_info(token: str) -> dict:
    url = "https://login.yandex.ru/info"
    headers = {"Authorization": f"OAuth {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        user_info = response.json()

        return {
            'id': user_info.get('id'),
            'login': user_info.get('login'),
            'default_email': user_info.get('default_email'),
            'first_name': user_info.get('first_name', ''),
            'last_name': user_info.get('last_name', ''),
            'display_name': user_info.get('display_name', '')
        }
    except requests.RequestException as e:
        print(f"Error obtaining Yandex user info: {e}")
        return None
