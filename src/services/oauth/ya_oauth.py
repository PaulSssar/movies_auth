from base_oauth import BaseOAuth
from core.config import settings

class YandexOAuth(BaseOAuth):
    user_info_url = "https://login.yandex.ru/info"

    def __init__(self):
        super().__init__(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            redirect_uri=settings.redirect_uri
        )
    def parse_user_info(self, user_info: dict) -> dict:
        return {
            'id': user_info.get('id'),
            'login': user_info.get('login'),
            'default_email': user_info.get('default_email'),
            'first_name': user_info.get('first_name', ''),
            'last_name': user_info.get('last_name', ''),
            'display_name': user_info.get('display_name', '')
        }