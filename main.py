from src.NetworkSecurity.components.data_ingestion import DataIngestion
from src.NetworkSecurity.components.data_validation import DataValidation
from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging

from src.NetworkSecurity.entity.config import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        data_ingestion_artifact = data_ingestion.run_data_ingestion()
        logging.info("Data ingestion completed successfully.")

        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=data_validation_config)
        data_validation.initiate_data_validation()
        logging.info("Data validation completed successfully.")
    except NetworkSecurityException as e:
        logging.error(f"NetworkSecurityException occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")