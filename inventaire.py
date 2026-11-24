import os
import requests
import json
from datetime import datetime
import sys

base = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")
netbox = os.environ.get("NETBOX_URL", "http://127.0.0.1:8080")
jeton = os.environ["NETBOX_TOKEN"]
session = requests.Session()

try:
    reponses = session.get(f"{base}/containers/json?all=true", timeout=5)
except requests.exceptions.RequestException as e:
    sys.exit(f"Erreur : l'API Docker est injoignable sur {base}: {e}")

try:
    reponse = session.get(
        f"{netbox}/api/status/", headers={"Authorization": f"Bearer {jeton}"}, timeout=5
    )
except requests.exceptions.RequestException as e:
    sys.exit(f"Erreur : l'API NetBox est injoignable sur {netbox}: {e}")

version = reponse.json().get("netbox-version", "unknown")
print(f"NetBox version: {version}")
conteneurs = reponses.json()
url = f"{netbox}/api/core/object-types/?limit=50"
total = 0
releve = []

while url is not None:
    page = session.get(
        url, headers={"Authorization": f"Bearer {jeton}"}, timeout=5
    ).json()
    total += len(page["results"])
    url = page["next"]
print(f"Total object types in NetBox: {total} (NetBox annonce {page['count']})")
for conteneur in conteneurs:
    infos = {
        "id": conteneur["Id"],
        "name": conteneur["Names"][0].lstrip("/"),
        "image": conteneur["Image"],
        "state": conteneur["State"],
    }
    print(
        f"ID: {conteneur['Id']}, Name: {conteneur['Names'][0].lstrip('/')}, Image: {conteneur['Image']}, State: {conteneur['State']}"
    )

    if conteneur["State"] == "running":
        stats = session.get(
            f"{base}/containers/{conteneur['Id']}/stats?stream=false", timeout=5
        ).json()
        cpu, avant = stats["cpu_stats"], stats["precpu_stats"]
        delta_cpu = cpu["cpu_usage"]["total_usage"] - avant["cpu_usage"]["total_usage"]
        delta_systeme = cpu["system_cpu_usage"] - avant.get("system_cpu_usage", 0)
        pourcent = (
            delta_cpu / delta_systeme * cpu["online_cpus"] * 100
            if delta_systeme
            else 0.0
        )
        infos["cpu_percent"] = pourcent
        infos["memory_mb"] = stats["memory_stats"]["usage"] / 1024 / 1024
        print(f"   CPU : {pourcent:.1f} %  Mémoire : {infos['memory_mb']:.1f} Mo")
    else:
        print(f"  Not running, last state: {conteneur['State']}")

    releve.append(infos)

with open("inventaire.json", "w") as f:
    json.dump(
        {
            "date": datetime.now().isoformat(),
            "conteneurs": releve,
            "version_netbox": version,
            "nb_types_objets": total,
        },
        f,
        indent=4,
    )
