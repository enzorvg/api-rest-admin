import os
import requests

base = os.environ.get("DOCKER_API_URL", "http://127.0.0.1:2375")

session = requests.Session()

reponses = session.get(f"{base}/containers/json?all=true", timeout=5)
conteneurs = reponses.json()

for conteneur in conteneurs:
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
        memoire_mo = stats["memory_stats"]["usage"] / 1024 / 1024
        print(f"   CPU : {pourcent:.1f} %  Mémoire : {memoire_mo:.1f} Mo")
    else:
        print(f"  Not running, last state: {conteneur['State']}")
