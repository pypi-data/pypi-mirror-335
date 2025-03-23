import requests

class Py2SecMail:
    BASE_URL = "https://2secmail.cloud/api/"
    API_KEY = "6sVhoPMjTwEZk57t3YyVXhiwPVT7NT"  # Clé API incluse par défaut

    @classmethod
    def get_domains(cls, domain_type="all"):
        """Récupère la liste des domaines disponibles."""
        url = f"{cls.BASE_URL}domains/{cls.API_KEY}/{domain_type}"
        response = requests.get(url)
        return response.json()

    @classmethod
    def create_email(cls):
        """Crée un nouvel email temporaire."""
        url = f"{cls.BASE_URL}emails/{cls.API_KEY}"
        response = requests.post(url)
        return response.json()

    @classmethod
    def update_email(cls, current_email, new_username, new_domain):
        """Modifie l'adresse email existante."""
        url = f"{cls.BASE_URL}emails/{cls.API_KEY}/{current_email}/{new_username}/{new_domain}"
        response = requests.post(url)
        return response.json()

    @classmethod
    def delete_email(cls, email):
        """Supprime un email temporaire."""
        url = f"{cls.BASE_URL}emails/{cls.API_KEY}/{email}"
        response = requests.post(url)
        return response.json()

    @classmethod
    def get_messages(cls, email):
        """Récupère les messages d'un email donné."""
        url = f"{cls.BASE_URL}messages/{cls.API_KEY}/{email}"
        response = requests.get(url)
        return response.json()

    @classmethod
    def get_message(cls, message_id):
        """Récupère un message spécifique."""
        url = f"{cls.BASE_URL}messages/{cls.API_KEY}/message/{message_id}"
        response = requests.get(url)
        return response.json()

    @classmethod
    def delete_message(cls, message_id):
        """Supprime un message spécifique."""
        url = f"{cls.BASE_URL}messages/{cls.API_KEY}/message/{message_id}"
        response = requests.post(url)
        return response.json()

    @classmethod
    def download_attachment(cls, hash_id, filename):
        """Télécharge une pièce jointe d'un email."""
        url = f"{cls.BASE_URL}d/{hash_id}/{filename}"
        response = requests.get(url, stream=True)
        return response.content if response.status_code == 200 else None

    @classmethod
    def token_to_email(cls, email_token):
        """Récupère l'email associé à un token."""
        return f"{cls.BASE_URL}token/{email_token}"
