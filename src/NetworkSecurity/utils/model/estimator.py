import os, sys

from src.NetworkSecurity.constants.training_pipeline import *
from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging

class NetworkModel:
    def __init__(self, preprocessor, model):
        self.model = model
        self.preprocessor = preprocessor

    def predict(self, X):
        try:
            transformed_data = self.preprocessor.transform(X)
            predictions = self.model.predict(transformed_data)
            return predictions
        except Exception as e:
            raise NetworkSecurityException(e)
    