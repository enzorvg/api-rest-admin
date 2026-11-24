import os
import requests
import json
from datetime import datetime

base = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")

session = requests.Session()

reponses = session.get(f"{base}/containers/json?all=true", timeout=5)
conteneurs = reponses.json()
releve = []
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
        {"date": datetime.now().isoformat(), "conteneurs": releve},
        f,
        indent=4,
    )
