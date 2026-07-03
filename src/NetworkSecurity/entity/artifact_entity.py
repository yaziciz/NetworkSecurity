from dataclasses import dataclass

@dataclass
class DataIngestionArtifactConfig:
    train_file_path: str
    test_file_path: str

@dataclass
class DataValidationArtifactConfig:
    validation_status: bool
    validated_train_file_path: str
    validated_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str


@dataclass
class DataTransformationArtifactConfig:
    transformed_train_file_path: str
    transformed_test_file_path: str
    preprocessed_object_file_path: str


@dataclass
class ClassificationMetricArtifactConfig:
    f1_score: float
    precision_score: float
    recall_score: float


@dataclass
class ModelTrainerArtifactConfig:
    model_file_path: str
    training_metric_artifact: ClassificationMetricArtifactConfig
    testing_metric_artifact: ClassificationMetricArtifactConfig