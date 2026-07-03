import sys
import os
import numpy as np
import pandas as pd
import mlflow

from src.NetworkSecurity.logging.logger import logging
from src.NetworkSecurity.exception.exception import NetworkSecurityException

from src.NetworkSecurity.constants.training_pipeline import *
from src.NetworkSecurity.entity.artifact_entity import DataTransformationArtifactConfig, ModelTrainerArtifactConfig, ClassificationMetricArtifactConfig
from src.NetworkSecurity.entity.config import ModelTrainerConfig
from src.NetworkSecurity.utils.common import save_numpy_array, load_numpy_array, save_object, load_object

from src.NetworkSecurity.utils.metric.classification_metrics import get_classification_metrics
from src.NetworkSecurity.utils.model.estimator import NetworkModel

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier

from src.NetworkSecurity.utils.common import evaluate_models

import dagshub
dagshub.init(repo_owner='ziyaatayazici', repo_name='NetworkSecurity', mlflow=True)
#mlflow.autolog()

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifactConfig):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def track_mlflow(self, model, training_metric: ClassificationMetricArtifactConfig, model_file_path: str = None):
        with mlflow.start_run() as run:
            mlflow.log_param("model_name", model.__class__.__name__)
            mlflow.log_metric("f1_score", training_metric.f1_score)
            mlflow.log_metric("precision_score", training_metric.precision_score)
            mlflow.log_metric("recall_score", training_metric.recall_score)

            model_metadata = None
            if model_file_path is not None:
                model_metadata = {"model_save_path": model_file_path}

            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=model.__class__.__name__,
                metadata=model_metadata,
            )
            if model_file_path is not None:
                mlflow.log_artifact(model_file_path, artifact_path="serialized_model")
    
    
    def train_model(self, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray = None, y_test: np.ndarray = None) -> ModelTrainerArtifactConfig:
        try:
            models = {
                "LogisticRegression": LogisticRegression(verbose=1),
                "KNeighborsClassifier": KNeighborsClassifier(),
                "DecisionTreeClassifier": DecisionTreeClassifier(),
                "RandomForestClassifier": RandomForestClassifier(verbose=1),
                "GradientBoostingClassifier": GradientBoostingClassifier(verbose=1), 
                "AdaBoostClassifier": AdaBoostClassifier()
            }

            params = {
                "DecisionTreeClassifier": {
                    'criterion': ['gini', 'entropy', 'log_loss'],
                    # 'splitter': ['best', 'random'],
                    # 'max_features': ['sqrt', 'log2']
                },
                "RandomForestClassifier": {
                    # 'criterion': ['gini', 'entropy', 'log_loss'],
                    # 'max_features': ['sqrt', 'log2', None],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "GradientBoostingClassifier": {
                    'learning_rate': [0.1, 0.01, 0.05, 0.001],
                    'subsample': [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    'n_estimators': [8, 16, 32, 64, 128, 256],
                    # 'criterion': ['squared_error', 'friedman_mse'],
                    # 'max_features': ['auto', 'sqrt', 'log2'],
                },
                "AdaBoostClassifier": {
                    'learning_rate': [0.1, 0.01, 0.05, 0.001],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "LogisticRegression": {}
            }

            model_report: dict = evaluate_models(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test, models=models, params=params)

            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = models[best_model_name]

            preprocessor = load_object(file_path=self.data_transformation_artifact.preprocessed_object_file_path)
            model_dir_path = os.path.dirname(self.model_trainer_config.model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(file_path=self.model_trainer_config.model_file_path, obj=Network_Model)

            y_train_pred = best_model.predict(x_train)
            training_metric = get_classification_metrics(y_true=y_train, y_pred=y_train_pred)

            self.track_mlflow(best_model, training_metric, self.model_trainer_config.model_file_path)

            y_test_pred = best_model.predict(x_test)
            testing_metric = get_classification_metrics(y_true=y_test, y_pred=y_test_pred)

            self.track_mlflow(best_model, testing_metric)

            save_object("models/model_best.pkl", best_model)

            model_trainer_artifact = ModelTrainerArtifactConfig(
                model_file_path=self.model_trainer_config.model_file_path,
                training_metric_artifact=ClassificationMetricArtifactConfig(
                    f1_score=training_metric.f1_score,
                    precision_score=training_metric.precision_score,
                    recall_score=training_metric.recall_score
                ),
                testing_metric_artifact=ClassificationMetricArtifactConfig(
                    f1_score=testing_metric.f1_score,
                    precision_score=testing_metric.precision_score,
                    recall_score=testing_metric.recall_score
                )
            )
            
            return  model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_model_trainer(self) -> ModelTrainerArtifactConfig:
        try:
            logging.info("Loading transformed training and testing datasets")
            transformed_train_file_path = self.data_transformation_artifact.transformed_train_file_path
            transformed_test_file_path = self.data_transformation_artifact.transformed_test_file_path

            train_array = load_numpy_array(transformed_train_file_path)
            test_array = load_numpy_array(transformed_test_file_path)

            x_train, y_train = train_array[:, :-1], train_array[:, -1]
            x_test, y_test = test_array[:, :-1], test_array[:, -1]

            logging.info("Training the model")
            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)

            logging.info(f"Model Trainer Artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

