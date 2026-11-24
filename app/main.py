import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()
base = os.environ["DOCKER_API_URL"]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/containers")
def get_containers():
    response = requests.get(f"{base}/containers/json?all=true")
    conteneurs = response.json()

    geres = []
    for conteneur in conteneurs:
        labels = conteneur["Labels"]
        if labels.get("adminapi.managed") == "true":
            geres.append(
                {
                    "id": conteneur["Id"],
                    "name": conteneur["Names"][0].lstrip("/"),
                    "image": conteneur["Image"],
                    "state": conteneur["State"],
                }
            )
    return geres


@app.get("/containers/{container_id}")
def get_container(container_id: str):
    response = requests.get(f"{base}/containers/{container_id}/json")
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Container not found"
        )
    conteneur = response.json()
    labels = conteneur["Config"]["Labels"]
    if labels.get("adminapi.managed") == "true":
        return {
            "id": conteneur["Id"],
            "name": conteneur["Name"].lstrip("/"),
            "image": conteneur["Config"]["Image"],
            "state": conteneur["State"]["Status"],
        }
    else:
        raise HTTPException(status_code=404, detail="Container not managed by adminapi")
