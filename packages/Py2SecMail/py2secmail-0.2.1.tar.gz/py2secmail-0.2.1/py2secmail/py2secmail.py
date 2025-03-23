import requests

# Initialisation de la classe
api = Py2SecMail()

# Récupérer la liste des domaines disponibles
domains = api.get_domains("all")
print(domains)

# Créer un nouvel email temporaire
new_email = api.create_email()
print(new_email)

# Modifier une adresse email existante
updated_email = api.update_email("old@example.com", "newuser", "newexample.com")
print(updated_email)

# Supprimer un email temporaire
delete_response = api.delete_email("old@example.com")
print(delete_response)

# Récupérer les messages d'un email donné
messages = api.get_messages("example@example.com")
print(messages)

# Récupérer un message spécifique par son ID
message = api.get_message_by_id("ap94AWDg123ELQz07vrVB9dLXlbqZM5NGwYxOJKko8n6m1")
print(message)

# Supprimer un message spécifique par son ID
delete_message_response = api.delete_message_by_id("ap94AWDg123ELQz07vrVB9dLXlbqZM5NGwYxOJKko8n6m1")
print(delete_message_response)

# Télécharger une pièce jointe d'un email
attachment = api.download_attachment("abc123", "filename.pdf")
with open("filename.pdf", "wb") as f:
    f.write(attachment)

# Récupérer l'email associé à un token
email_url = api.token_to_email("email_token")
print(email_url)
