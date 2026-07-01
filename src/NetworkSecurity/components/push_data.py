import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MOBGO_DB_URL = os.getenv("MONGO_DB_URL")
print(f"MOBGO_DB_URL: {MOBGO_DB_URL}")

import certifi
ca=certifi.where()
print(f"ca: {ca}")

import pandas as pd
import numpy as np
import pymongo
from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging

class NetworkDataExtract():
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MOBGO_DB_URL, tlsCAFile=ca)
            logging.info("MongoDB connection established successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json(self, csv_file_path: str):
        try:
            df = pd.read_csv(csv_file_path)
            df.reset_index(drop=True, inplace=True)
            records = list(json.loads(df.T.to_json()).values())
            return records
        except Exception as e:
            logging.error(f"Failed to convert {csv_file_path} to JSON: {e}")
            raise NetworkSecurityException(e, sys)

    def insert_data_to_mongodb(self, json_data: list, db_name: str, collection_name: str):
        try:
            if not json_data:
                raise ValueError("json_data must be a non-empty list")

            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            result = self.collection.insert_many(json_data)
            logging.info(f"Inserted data into MongoDB collection: {collection_name} in database: {db_name}.")
            return len(result.inserted_ids)
        except Exception as e:
            logging.error(f"Failed to insert data into MongoDB: {e}")
            raise NetworkSecurityException(e, sys)
        
if __name__ == "__main__":
    FILE_PATH = "data/phisingData.csv"
    DATABASE_NAME = "NetworkSecurity"
    COLLECTION_NAME = "PhishingData"

    NetworkDataExtractObj = NetworkDataExtract()
    json_record = NetworkDataExtractObj.csv_to_json(FILE_PATH)
    numrecords = NetworkDataExtractObj.insert_data_to_mongodb(json_record, DATABASE_NAME, COLLECTION_NAME)

    print(f"Number of records inserted: {numrecords}")
