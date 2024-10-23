import http
import json
import enum
import logging

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(str, enum.Enum):
    ADMIN = enum.auto()
    SUBSCRIBER = enum.auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        payload = {'login': username, 'password': password}
        data = self.get_data_from_auth_service('signin', payload)

        if not data:
            return None

        payload = {'token': data.get('token')}
        logging.info(f'_______________________________________________________{payload}')
        data = self.get_data_from_auth_service('check_token', payload)

        logging.info(f'_______________________________________________________{data}')

        user, created = User.objects.get_or_create(id=data['id'], )
        user.email = data.get('email')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.is_admin = data.get('role') == Roles.ADMIN
        user.is_active = data.get('is_superuser')
        user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_data_from_auth_service(url_prefix, payload):
        url = settings.AUTH_API_LOGIN_URL + url_prefix
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None
        return response.json()
