import uuid


def generate_api_key():
    """Génère une clé API unique."""
    return str(uuid.uuid4())

# WATCHMAN_TOKEN="pypi-AgEIcHlwaS5vcmcCJDlhNWIzMGU0LTg4YWEtNDA1OS1hYTljLTYzMDNjZjMzOTEzMgACKlszLCI0MzNlMTdmZS1hYjA1LTRiZTQtOWYyZC02MTBkZWQ0OGMxYWEiXQAABiCdK27YWRUo5o-ZFFyo-8zWJeb9GS2cQ7DG9B6V9BqrpQ"

if __name__ == "__main__":
    api_key = generate_api_key()
    print(f"Votre clé API générée est : {api_key}")
