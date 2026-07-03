from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging

from src.NetworkSecurity.entity.config import DataIngestionConfig
from src.NetworkSecurity.entity.artifact_entity import DataIngestionArtifactConfig

import os
import sys
import numpy as np
import pymongo
import certifi
from typing import List
import pandas as pd
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
TLS_CA_FILE = certifi.where()

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
            self.client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=TLS_CA_FILE)
            logging.info("MongoDB connection established successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise NetworkSecurityException(e, sys)
        
    def run_data_ingestion(self) -> DataIngestionArtifactConfig:
        try:
            # Fetch data from MongoDB
            data = self.fetch_data_from_mongodb()
            data = self.export_data_to_csv(data)
            train_data, test_data = self.split_data(data, test_size=self.data_ingestion_config.train_test_split_ratio)

            artifactConfig = DataIngestionArtifactConfig(
                train_file_path=self.data_ingestion_config.train_file_path,
                test_file_path=self.data_ingestion_config.test_file_path
            )

            print(f"train_file_path: {artifactConfig.train_file_path}") 
            print(f"test_file_path: {artifactConfig.test_file_path}")

            # Save train and test data to CSV files
            os.makedirs(os.path.dirname(artifactConfig.train_file_path), exist_ok=True)
            train_data.to_csv(artifactConfig.train_file_path, index=False)
            os.makedirs(os.path.dirname(artifactConfig.test_file_path), exist_ok=True)
            test_data.to_csv(artifactConfig.test_file_path, index=False)

            logging.info(f"Data ingestion completed successfully. Train and test data saved to {self.data_ingestion_config.ingested_dir}.")
            return artifactConfig
        except Exception as e:
            logging.error(f"Data ingestion failed: {e}")
            raise NetworkSecurityException(e, sys)

    def fetch_data_from_mongodb(self) -> List[dict]:
        try:
            db_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            db = self.client[db_name]
            collection = db[collection_name]
            data = pd.DataFrame(list(collection.find()))
            
            if "_id" in data.columns.to_list():
                data.drop(columns=["_id"], inplace=True)

            data.replace({"na": np.nan}, inplace=True)

            logging.info(f"Fetched {len(data)} records from MongoDB collection: {collection_name} in database: {db_name}.")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch data from MongoDB: {e}")
            raise NetworkSecurityException(e, sys)
        
    def export_data_to_csv(self, data: pd.DataFrame):
        try:
            file_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            data.to_csv(file_path, index=False)
            logging.info(f"Exported data to CSV file at: {file_path}.")
            return data
        except Exception as e:
            logging.error(f"Failed to export data to CSV: {e}")
            raise NetworkSecurityException(e, sys)

    def split_data(self, data: List[dict], test_size: float = 0.2, random_state: int = 42):
        try:
            train_data, test_data = train_test_split(data, test_size=test_size, random_state=random_state)
            logging.info(f"Split data into train and test sets with test size: {test_size}.")
            return train_data, test_data
        except Exception as e:
            logging.error(f"Failed to split data: {e}")
            raise NetworkSecurityException(e, sys)