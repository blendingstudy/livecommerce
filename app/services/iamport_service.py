# app/services/iamport_service.py

import socket
import requests
from flask import current_app, json
import time

class IamportService:
    """ BASE_URL = "https://43.203.65.5"

    def __init__(self):
        self.imp_key = current_app.config['IAMPORT_API_KEY']
        self.imp_secret = current_app.config['IAMPORT_API_SECRET']
        self.access_token = None
        self.expired_at = 0
        #self.session = requests.Session()

    def _get_token(self):
        print("Entering _get_token method")
        now = int(time.time())
        if now < self.expired_at:
            return self.access_token
    
        url = "https://43.203.65.5/users/getToken"

        payload = {
            "imp_key": self.imp_key,
            "imp_secret": self.imp_secret
        }
        headers = {"Content-Type": "application/json"}

        print('hello')
        print('Sending request to:', url)
        print('Payload:', payload)
        try:    
            response = requests.request("post", url, json=payload, headers=headers, verify=False, timeout=30)
            print('Response status:', response.status_code)
            print('Response content:', response.text)
            response.raise_for_status()
            result = response.json()
            print('received result')
            
            self.access_token = result['response']['access_token']
            self.expired_at = now + result['response']['expire_at']

            return self.access_token
        except requests.RequestException as e:
            print(f"API request failed: {str(e)}")
            raise
        except requests.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")
            raise
        except KeyError as e:
            print(f"Expected key not found in response: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise """
    BASE_URL = "https://api.iamport.kr"
    
    def __init__(self):
        self.imp_key = current_app.config['IAMPORT_API_KEY']
        self.imp_secret = current_app.config['IAMPORT_API_SECRET']
        self.access_token = None
        self.expired_at = 0
        #self.session = requests.Session()

    def _get_token(self):
        original_getaddrinfo = socket.getaddrinfo

        def getaddrinfo(*args, **kwargs):
            return original_getaddrinfo(*args, **kwargs)

        socket.getaddrinfo = getaddrinfo

        url = "https://api.iamport.kr/users/getToken"
        payload = {
            "imp_key": "0054575041252252",
            "imp_secret": "4y5PCQ5KoXFWRL7UltBruL2pvSnux1jjVFwo2L5hFqCNYH4AJGjXsCPbmGezWzwnWkHNP7Uv4ApDwb4w"
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response.status_code)
        print(response.text)

    def find_payment(self, imp_uid):
        print("find_payment")
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