from src.NetworkSecurity.entity.artifact_entity import DataIngestionArtifactConfig, DataValidationArtifactConfig
from src.NetworkSecurity.entity.config import DataValidationConfig

from src.NetworkSecurity.exception.exception import NetworkSecurityException
from src.NetworkSecurity.logging.logger import logging
from src.NetworkSecurity.constants.training_pipeline import *
from src.NetworkSecurity.utils.common import read_yaml_file, write_yaml_file

from scipy.stats import ks_2samp
import os
import sys
import pandas as pd

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifactConfig, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            logging.error(f"Error initializing DataValidation: {e}")
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_num_columns = len(self._schema_config['columns'])
            actual_num_columns = dataframe.shape[1]
            if expected_num_columns != actual_num_columns:
                logging.error(f"Number of columns mismatch. Expected: {expected_num_columns}, Actual: {actual_num_columns}")
                return False
            return True
        except Exception as e:
            logging.error(f"Error validating number of columns: {e}")
            raise NetworkSecurityException(e, sys)
        
    def check_data_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.05) -> bool:
        try:
            drift_report = {}
            drift_detected_any = False
            for column in base_df.columns:
                if column in current_df.columns:
                    base_data = base_df[column].dropna()
                    current_data = current_df[column].dropna()
                    _, p_value = ks_2samp(base_data, current_data)
                    p_value = float(p_value)
                    drift_detected = bool(p_value < threshold)
                    drift_detected_any = drift_detected_any or drift_detected
                    drift_report[column] = {
                        "p_value": p_value,
                        "drift_detected": drift_detected
                    }
                else:
                    logging.warning(f"Column {column} not found in current dataframe.")

            status = not drift_detected_any

            #save drift report to file
            write_yaml_file(self.data_validation_config.drift_report_file_path, drift_report)
            logging.info(f"Data drift report saved to {self.data_validation_config.drift_report_file_path}")
            return status
        except Exception as e:
            logging.error(f"Error checking data drift: {e}")
            raise NetworkSecurityException(e, sys)
   
    def initiate_data_validation(self) -> DataValidationArtifactConfig:
        try:
            # Load the ingested train and test data
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            status_train = self.validate_number_of_columns(train_df)
            status_test = self.validate_number_of_columns(test_df)

            if not status_train or not status_test:
                logging.error("Data validation failed due to column mismatch.")


            # Check for data drift
            status = self.check_data_drift(base_df=train_df, current_df=test_df)

            #save the validated train and test data to the specified paths
            os.makedirs(os.path.dirname(self.data_validation_config.validated_train_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(self.data_validation_config.validated_test_file_path), exist_ok=True)
            train_df.to_csv(self.data_validation_config.validated_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.validated_test_file_path, index=False)

            return DataValidationArtifactConfig(
                validation_status=status,
                validated_train_file_path=self.data_validation_config.validated_train_file_path,
                validated_test_file_path=self.data_validation_config.validated_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
        except Exception as e:
            logging.error(f"Error during data validation: {e}")
            raise NetworkSecurityException(e, sys)