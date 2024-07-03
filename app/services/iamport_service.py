# app/services/iamport_service.py

import requests
from flask import current_app
import time

class IamportService:
    BASE_URL = "https://api.iamport.kr"

    def __init__(self):
        self.imp_key = current_app.config['IAMPORT_API_KEY']
        self.imp_secret = current_app.config['IAMPORT_API_SECRET']
        self.access_token = None
        self.expired_at = 0

    def _get_token(self):
        now = int(time.time())
        if now < self.expired_at:
            return self.access_token

        url = f"{self.BASE_URL}/users/getToken"
        data = {
            'imp_key': self.imp_key,
            'imp_secret': self.imp_secret
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()

        self.access_token = result['response']['access_token']
        self.expired_at = now + result['response']['expire_at']

        return self.access_token

    def find_payment(self, imp_uid):
        token = self._get_token()
        url = f"{self.BASE_URL}/payments/{imp_uid}"
        headers = {'Authorization': token}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

        if result['code'] != 0:
            raise Exception(result['message'])

        return result['response']

    def cancel_payment(self, imp_uid, amount, reason):
        token = self._get_token()
        url = f"{self.BASE_URL}/payments/cancel"
        headers = {'Authorization': token}
        data = {
            'imp_uid': imp_uid,
            'amount': amount,
            'reason': reason
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()

        if result['code'] != 0:
            raise Exception(result['message'])

        return result['response']