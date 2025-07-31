from fastapi import FastAPI
import requests
import pandas as pd
from app.optimizer import moga_optimize
from prometheus_fastapi_instrumentator import Instrumentator
import os
import logging

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {"message": "MOGA Optimizer Microservice running!"}

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/optimize")
def optimize():
    logging.info("Received request to /optimize")
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service.default.svc.cluster.local:8000/generate-catalog")
    logging.info(f"Using AUTH_SERVICE_URL: {AUTH_SERVICE_URL}")
    
    try:
        response = requests.get(AUTH_SERVICE_URL, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error reaching AUTH_SERVICE_URL: {AUTH_SERVICE_URL} | Exception: {str(e)}")
        return {"error": f"Could not reach catalog service: {str(e)}"}
    if response.status_code != 200:
        logging.error(f"Catalog fetch failed with code {response.status_code}")
        return {"error": "Failed to fetch catalog"}

    logging.info(f"Catalog JSON: {response.text}")
    try:
        catalog = pd.DataFrame(response.json())
        logging.info(f"Parsed DataFrame:\n{catalog}")
    except Exception as e:
        logging.exception("Failed to convert catalog JSON to DataFrame")
        return {"error": f"Catalog parsing failed: {str(e)}"}

    try:
        result = moga_optimize(catalog)
    except Exception as e:
        logging.exception("Optimization failed")
        return {"error": f"MOGA optimization failed: {str(e)}"}

    os.makedirs("/app/plot_data", exist_ok=True)
    return result
