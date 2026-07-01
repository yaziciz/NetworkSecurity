from src.NetworkSecurity.components.data_ingestion import DataIngestion
from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging

from src.NetworkSecurity.entity.config import TrainingPipelineConfig, DataIngestionConfig

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        data_ingestion.run_data_ingestion()
    except NetworkSecurityException as e:
        logging.error(f"NetworkSecurityException occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")