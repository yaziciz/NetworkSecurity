import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from src.NetworkSecurity.logging.logger import logging
from src.NetworkSecurity.exception.exception import NetworkSecurityException

from src.NetworkSecurity.constants.training_pipeline import *
from src.NetworkSecurity.entity.artifact_entity import DataValidationArtifactConfig, DataTransformationArtifactConfig
from src.NetworkSecurity.entity.config import DataTransformationConfig
from src.NetworkSecurity.utils.common import save_numpy_array, load_numpy_array, save_object, load_object


class DataTransformation:
    def __init__(self, data_transformation_config: DataTransformationConfig, data_validation_artifact: DataValidationArtifactConfig):
        try:
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def run(self) -> DataTransformationArtifactConfig:
        logging.info("Starting data transformation process.")
        try:
            # Load validated train and test data
            train_df = pd.read_csv(self.data_validation_artifact.validated_train_file_path)
            test_df = pd.read_csv(self.data_validation_artifact.validated_test_file_path)

            # Separate features and target variable
            X_train = train_df.drop(columns=[TARGET_COLUMN])
            y_train = train_df[TARGET_COLUMN]
            X_test = test_df.drop(columns=[TARGET_COLUMN])
            y_test = test_df[TARGET_COLUMN]

            # Define the preprocessing pipeline
            logging.info("Creating preprocessing pipeline with KNNImputer.")
            preprocessing_pipeline = Pipeline(steps=[
                ('imputer', KNNImputer(**DATA_TRANSFORMATION_INPUT_PARAMS)),
                # Add more preprocessing steps here if needed
            ])

            # Fit the pipeline on the training data and transform both train and test data
            X_train_transformed = preprocessing_pipeline.fit_transform(X_train)
            X_test_transformed = preprocessing_pipeline.transform(X_test)

            # Save the transformed data and the preprocessing object
            save_numpy_array(self.data_transformation_config.transformed_train_file_path, np.c_[X_train_transformed, y_train.values])
            save_numpy_array(self.data_transformation_config.transformed_test_file_path, np.c_[X_test_transformed, y_test.values])
            save_object(self.data_transformation_config.preprocessed_object_file_path, preprocessing_pipeline)

            logging.info("Data transformation process completed successfully.")

            return DataTransformationArtifactConfig(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                preprocessed_object_file_path=self.data_transformation_config.preprocessed_object_file_path
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        