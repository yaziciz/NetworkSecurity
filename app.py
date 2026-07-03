import sys
from dotenv import load_dotenv

from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging
from src.NetworkSecurity.pipeline.training_pipeline import TrainingPipeline
from src.NetworkSecurity.utils.common import save_object, load_object

from src.NetworkSecurity.entity.config import TrainingPipelineConfig
from src.NetworkSecurity.constants.training_pipeline import *

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, File, UploadFile
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse

import pandas as pd

"""
import os
import pymongo
import certifi

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
    
if __name__ == "__main__":
    app_run(app, host="localhost", port=8000, reload=True)


