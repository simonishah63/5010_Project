from fastapi import FastAPI
import requests
import pandas as pd
from app.optimizer import moga_optimize
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

AUTH_SERVICE_URL = "http://auth-service.default.svc.cluster.local/generate-catalog"

@app.get("/")
def root():
    return {"message": "MOGA Optimizer Microservice running!"}

@app.get("/optimize")
def optimize():
    response = requests.get(AUTH_SERVICE_URL)
    if response.status_code != 200:
        return {"error": "Failed to fetch catalog"}
    catalog = pd.DataFrame(response.json())
    result = moga_optimize(catalog)
    return result
