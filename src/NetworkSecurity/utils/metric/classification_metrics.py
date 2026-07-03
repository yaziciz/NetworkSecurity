from src.NetworkSecurity.entity.artifact_entity import ClassificationMetricArtifactConfig
from src.NetworkSecurity.exception.exception import NetworkSecurityException
from sklearn.metrics import f1_score, precision_score, recall_score

def get_classification_metrics(y_true, y_pred) -> ClassificationMetricArtifactConfig:
    try:
        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)

        return ClassificationMetricArtifactConfig(
            f1_score=f1,
            precision_score=precision,
            recall_score=recall
        )
    except Exception as e:
        raise NetworkSecurityException(e)