import os
import sys

from src.NetworkSecurity.logging.logger import logging
from src.NetworkSecurity.exception.exception import NetworkSecurityException

from src.NetworkSecurity.components.data_ingestion import DataIngestion
from src.NetworkSecurity.components.data_transformation import DataTransformation
from src.NetworkSecurity.components.data_validation import DataValidation
from src.NetworkSecurity.components.model_trainer import ModelTrainer

from src.NetworkSecurity.entity.config import TrainingPipelineConfig, DataIngestionConfig, DataTransformationConfig, DataValidationConfig, ModelTrainerConfig
from src.NetworkSecurity.entity.artifact_entity import DataIngestionArtifactConfig, DataTransformationArtifactConfig, DataValidationArtifactConfig, ModelTrainerArtifactConfig

class TrainingPipeline:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        try:
            self.training_pipeline_config = training_pipeline_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_data_ingestion(self) -> DataIngestionArtifactConfig:
        try:
            logging.info("Starting data ingestion...")
            data_ingestion_config = DataIngestionConfig(self.training_pipeline_config)
            data_ingestion = DataIngestion(data_ingestion_config)
            logging.info("Data ingestion completed successfully.")
            return data_ingestion.run_data_ingestion()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_data_validation(self, data_ingestion_artifact: DataIngestionArtifactConfig) -> DataValidationArtifactConfig:
        try:
            logging.info("Starting data validation...")
            data_validation_config = DataValidationConfig(self.training_pipeline_config)
            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config,
            )
            logging.info("Data validation completed successfully.")
            return data_validation.initiate_data_validation()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_data_transformation(self, data_validation_artifact: DataValidationArtifactConfig) -> DataTransformationArtifactConfig:
        try:
            logging.info("Starting data transformation...")
            data_transformation_config = DataTransformationConfig(self.training_pipeline_config)
            data_transformation = DataTransformation(
                data_transformation_config=data_transformation_config,
                data_validation_artifact=data_validation_artifact,
            )
            logging.info("Data transformation completed successfully.")
            return data_transformation.run()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_model_trainer(self, data_transformation_artifact: DataTransformationArtifactConfig) -> ModelTrainerArtifactConfig:
        try:
            logging.info("Starting model training...")
            model_trainer_config = ModelTrainerConfig(self.training_pipeline_config)
            model_trainer = ModelTrainer(
                model_trainer_config=model_trainer_config,
                data_transformation_artifact=data_transformation_artifact,
            )
            logging.info("Model training completed successfully.")
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.run_data_ingestion()
            data_validation_artifact = self.run_data_validation(data_ingestion_artifact)
            data_transformation_artifact = self.run_data_transformation(data_validation_artifact)
            self.run_model_trainer(data_transformation_artifact)
            logging.info("Training pipeline completed successfully.")
        except Exception as e:
            raise NetworkSecurityException(e, sys)