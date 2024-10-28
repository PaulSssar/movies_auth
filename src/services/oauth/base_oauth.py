import requests


class BaseOAuth:
    user_info_url = ""

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def get_user_info(self, token: str) -> dict:
        headers = {"Authorization": f"OAuth {token}"}

        try:
            response = requests.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()
            return self.parse_user_info(user_info)
        except requests.RequestException as e:
            print(f"Error obtaining user info: {e}")
            return None

    def parse_user_info(self, user_info: dict) -> dict:
        raise NotImplementedError(
            "This method should be overridden in subclasses")
