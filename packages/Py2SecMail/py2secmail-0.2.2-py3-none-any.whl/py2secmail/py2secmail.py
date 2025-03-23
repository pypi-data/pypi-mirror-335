import requests

class Py2SecMail:
    BASE_URL = "http://2secmail.cloud/api"
    API_KEY = "6sVhoPMjTwEZk57t3YyVXhiwPVT7NT"

    def __init__(self, api_key=API_KEY):
        self.api_key = api_key

    def get_domains(self, domain_type="all"):
        response = requests.get(f"{self.BASE_URL}/domains/{self.api_key}/{domain_type}")
        return response.json() if response.status_code == 200 else None

    def create_email(self):
        response = requests.post(f"{self.BASE_URL}/emails/{self.api_key}")
        return response.json() if response.status_code == 200 else None

    def update_email(self, email, username, domain):
        response = requests.post(f"{self.BASE_URL}/emails/{self.api_key}/{email}/{username}/{domain}")
        return response.json() if response.status_code == 200 else None

    def delete_email(self, email):
        response = requests.post(f"{self.BASE_URL}/emails/{self.api_key}/{email}")
        return response.json() if response.status_code == 200 else None

    def get_messages(self, email):
        response = requests.get(f"{self.BASE_URL}/messages/{self.api_key}/{email}")
        return response.json() if response.status_code == 200 else None

    def get_message_by_id(self, message_id):
        response = requests.get(f"{self.BASE_URL}/messages/{self.api_key}/message/{message_id}")
        return response.json() if response.status_code == 200 else None

    def delete_message_by_id(self, message_id):
        response = requests.post(f"{self.BASE_URL}/messages/{self.api_key}/message/{message_id}")
        return response.json() if response.status_code == 200 else None

    def download_attachment(self, hash_id, filename=None):
        url = f"{self.BASE_URL}/d/{hash_id}/{filename}" if filename else f"{self.BASE_URL}/d/{hash_id}"
        response = requests.get(url)
        return response.content if response.status_code == 200 else None

    def token_to_email(self, email_token):
        response = requests.get(f"{self.BASE_URL}/token/{email_token}")
        return response.json() if response.status_code == 200 else None
