import os
import sys
import pandas as pd

from src.NetworkSecurity.logging.logger import logging
from src.NetworkSecurity.exception.exception import NetworkSecurityException

from src.NetworkSecurity.utils.model.estimator import NetworkModel

from fastapi import File, UploadFile

from src.NetworkSecurity.utils.common import save_object, load_object

class BatchPredictionPipeline:
    def __init__(self, training_pipeline_config):
        try:
            self.training_pipeline_config = training_pipeline_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self, file: UploadFile = File(...)):
        try:
            df = pd.read_csv(file.file)
            if "Result" in df.columns:
                df = df.drop(columns=["Result"])
            logging.info("Batch prediction started successfully.")

            processor = load_object("models/preprocessor_best.pkl")
            model = load_object("models/model_best.pkl")
            network_model = NetworkModel(preprocessor=processor, model=model)
            
            y_pred = network_model.predict(df)
            df["predictions"] = y_pred
            logging.info("Batch prediction completed successfully.")

            df.to_csv("models/predictions/preds.csv", index=False)
            table_html = df.to_html(classes="table table-striped", index=False)
            return table_html
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
            
