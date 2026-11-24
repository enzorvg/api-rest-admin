from pydantic import BaseModel, Field
import os
import requests
from typing import Literal
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


class ConteneurACreer(BaseModel):
    name: str = Field(
        pattern=r"^[a-z][a-z0-9-]{1,30}$",
    )
    image: Literal["nginx:alpine", "httpd:alpine", "redis:alpine"] = Field()


@app.post("/containers", status_code=201)
def create_container(conteneur: ConteneurACreer):
    payload = {
        "Image": conteneur.image,
        "Labels": {"adminapi.managed": "true"},
    }

    response = requests.post(
        f"{base}/containers/create",
        params={"name": conteneur.name},
        json=payload,
    )
    if response.status_code == 409:
        raise HTTPException(
            status_code=409, detail="Ce nom de conteneur est déjà utilisé"
        )
    if response.status_code != 201:
        raise HTTPException(
            status_code=502, detail="Docker n'a pas pu créer le conteneur"
        )

    container_id = response.json()["Id"]

    start = requests.post(f"{base}/containers/{container_id}/start")
    if start.status_code != 204:
        raise HTTPException(
            status_code=502, detail="Docker n'a pas pu démarrer le conteneur"
        )

    return get_container(container_id)
