import os
import requests
from fastapi import FastAPI

app = FastAPI()
base = os.environ["DOCKER_API_URL"]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/containers")
def get_containers():
    response = requests.get(f"{base}/containers/json?all=true")
    return response.json()
