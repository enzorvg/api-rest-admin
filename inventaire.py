import os
import requests

base = os.environ.get("DOCKER_API_URL", "127.0.0.1")

session = requests.Session()

reponses = session.get(f"{base}/containers/json?all=true", timeout=5)
conteneurs = reponses.json()

for conteneur in conteneurs:
    print(
        f"ID: {conteneur['Id']}, Name: {conteneur['Names'][0].lstrip('/')}, Image: {conteneur['Image']}, State: {conteneur['State']}"
    )
