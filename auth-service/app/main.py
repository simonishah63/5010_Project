from fastapi import FastAPI
from app.microservice_catalog import generate_catalog
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {"message": "Authentication Microservice running!"}

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/generate-catalog")
def catalog():
    df = generate_catalog()
    return df.to_dict(orient="records")
