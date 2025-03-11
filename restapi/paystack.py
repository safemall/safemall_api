from django.conf import settings
import requests


class Paystack:
    secret_key = settings.PAYSTACK_SECRET_KEY
    base_url = 'https://api.paystack.co'

    @classmethod
    def initialize_transaction(cls, email, amount):
        """initialize deposit with Paystack"""

        url = f'{cls.base_url}/transaction/initialize'

        headers = {
            'Authorization': f'Bearer {cls.secret_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'email': email,
            'amount': int(amount * 100) #convert to kobo
        }

        response = requests.post(url, json=data, headers=headers)

        return response.json()
    

    @classmethod
    def verify_transaction(cls, reference):
        """Verify a transaction with Paystack"""

        url = f'{cls.base_url}/transaction/verify/{reference}'

        headers = {
            'Authorization': f'Bearer {cls.secret_key}'
        }

        response = requests.get(url, headers=headers)

        return response.json()


    @classmethod
    def create_transfer_recipient(cls, account_number, bank_code, recipient_name):

        headers = {
            'Authorization': f'Bearer {cls.secret_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'type': 'nuban',
            'name': recipient_name,
            'account_number': account_number,
            'bank_code': bank_code,
            'currency': 'NGN'
        }

        url = f'{cls.base_url}/transferrecipient'

        response = requests.post(url, headers=headers, json=data)

        return response
    

    @classmethod
    def initiate_transfer(cls, amount, recipient_code):

        url = f'{cls.base_url}/transfer'

        headers = {
            'Authorization': f'Bearer {cls.secret_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'source': 'balance',
            'amount': int(amount * 100) , #convert to kobo
            'currency': 'NGN',
            'recipient': recipient_code,
            'reason': 'Transfer to recipient'
        }

        response = requests.post(url, headers=headers, json=data)

        return response
    

    @classmethod
    def find_recipient(cls, account_number, bank_code):

        headers = {
            'Authorization': f'Bearer {cls.secret_key}'
        }

        url = f'{cls.base_url}/bank/resolve?account_number={account_number}&bank_code={bank_code}'

        response = requests.get(url, headers=headers)

        return response