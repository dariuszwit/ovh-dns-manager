import json

def load_users():
    """Ładuje listę użytkowników z pliku JSON."""
    with open("users.json") as f:
        return json.load(f)["users"]
