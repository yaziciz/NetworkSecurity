import sys

from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.pipeline.training_pipeline import TrainingPipeline

from src.NetworkSecurity.entity.config import TrainingPipelineConfig
from src.NetworkSecurity.constants.training_pipeline import *

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, File, UploadFile
from uvicorn import run as app_run
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

import pandas as pd

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

"""
import os
import pymongo
import certifi
from dotenv import load_dotenv

ca = certifi.where()
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(f"mongo_db_url: {mongo_db_url}")

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]
"""


app = FastAPI(title="Network Security API", version="1.0")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train", tags=["training"])
async def train_route():
    try:
        training_pipeline = TrainingPipeline(TrainingPipelineConfig())
        training_pipeline.run_pipeline()
        return {"message": "Training pipeline executed successfully."}
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
@app.post("/predict", tags=["prediction"])
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        from src.NetworkSecurity.pipeline.batch_predictions import BatchPredictionPipeline
        batch_prediction_pipeline = BatchPredictionPipeline(TrainingPipelineConfig())
        table_html = batch_prediction_pipeline.run_pipeline(file)
        return HTMLResponse(content=table_html)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
if __name__ == "__main__":
    app_run(app, host="localhost", port=8000, reload=True)


