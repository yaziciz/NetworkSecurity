from datetime import datetime
import os
from src.NetworkSecurity.constants.training_pipeline import *
from dataclasses import dataclass


@dataclass
class TrainingPipelineConfig:
    timestamp: str = datetime.now().strftime("%m%d%Y__%H%M%S")
    pipeline_name: str = PIPELINE_NAME
    artifact_name: str = ARTIFACT_DIR
    artifact_dir: str = os.path.join(artifact_name, timestamp)


class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_ingestion_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_INGESTION_DIR_NAME)
        self.feature_store_dir: str = os.path.join(self.data_ingestion_dir, DATA_INGESTION_FEATURE_STORE_DIR)
        self.feature_store_file_path: str = os.path.join(self.feature_store_dir, FILE_NAME)
        self.ingested_dir: str = os.path.join(self.data_ingestion_dir, DATA_INGESTION_INGESTED_DIR)
        self.train_file_path: str = os.path.join(self.ingested_dir, TRAIN_FILE_NAME)
        self.test_file_path: str = os.path.join(self.ingested_dir, TEST_FILE_NAME)
        self.collection_name: str = DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = DATA_INGESTION_DATABASE_NAME
        self.train_test_split_ratio: float = DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO


class DataValidationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_validation_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_VALIDATION_DIR_NAME)
        self.validated_dir: str = os.path.join(self.data_validation_dir, DATA_VALIDATION_VALID_DIR)
        self.validated_train_file_path: str = os.path.join(self.validated_dir, TRAIN_FILE_NAME)
        self.validated_test_file_path: str = os.path.join(self.validated_dir, TEST_FILE_NAME)
        self.invalid_dir: str = os.path.join(self.data_validation_dir, DATA_VALIDATION_INVALID_DIR)
        self.invalid_train_file_path: str = os.path.join(self.invalid_dir, TRAIN_FILE_NAME)
        self.invalid_test_file_path: str = os.path.join(self.invalid_dir, TEST_FILE_NAME)
        self.drift_report_file_path: str = os.path.join(self.data_validation_dir, DATA_VALIDATION_DRIFT_REPORT_DIR,
                                                        DATA_VALIDATION_DRIFT_REPORT_FILE_NAME)
        

class DataTransformationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_transformation_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_TRANSFORMATION_DIR_NAME)
        self.transformed_dir: str = os.path.join(self.data_transformation_dir, DATA_TRANSFORMATION_TRANSFORMED_DIR)
        self.transformed_train_file_path: str = os.path.join(self.transformed_dir, TRAIN_FILE_NAME.replace(".csv", ".npz"))
        self.transformed_test_file_path: str = os.path.join(self.transformed_dir, TEST_FILE_NAME.replace(".csv", ".npz"))
        self.preprocessed_object_file_path: str = os.path.join(self.data_transformation_dir, DATA_TRANSFORMATION_PREPROCESSED_DIR, PREPROCESSED_OBJECT_FILE_NAME)