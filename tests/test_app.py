"""
Unit tests for the FastAPI application exposing /, /train, and /predict.
"""

import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app import app

client = TestClient(app, raise_server_exceptions=False)


class TestIndexRoute:
    def test_root_redirects_to_docs(self):
        response = client.get("/", follow_redirects=False)

        assert response.status_code in (302, 307)
        assert response.headers["location"] == "/docs"


class TestTrainRoute:
    def test_train_success(self):
        with patch("app.TrainingPipeline") as MockPipeline, \
             patch("app.TrainingPipelineConfig") as MockConfig:

            mock_instance = MockPipeline.return_value
            mock_instance.run_pipeline.return_value = None

            response = client.get("/train")

            assert response.status_code == 200
            assert response.json() == {"message": "Training pipeline executed successfully."}
            MockPipeline.assert_called_once_with(MockConfig.return_value)
            mock_instance.run_pipeline.assert_called_once()

    def test_train_failure_raises_network_security_exception(self):
        with patch("app.TrainingPipeline") as MockPipeline, \
             patch("app.TrainingPipelineConfig"):

            MockPipeline.return_value.run_pipeline.side_effect = Exception("training blew up")

            response = client.get("/train")

            # Route re-raises as NetworkSecurityException -> unhandled -> 500
            assert response.status_code == 500


class TestPredictRoute:
    def test_predict_success_returns_html(self):
        fake_file = io.BytesIO(b"col1,col2\n1,2\n3,4")

        with patch(
            "src.NetworkSecurity.pipeline.batch_predictions.BatchPredictionPipeline"
        ) as MockBatchPipeline, \
             patch("app.TrainingPipelineConfig"):

            mock_instance = MockBatchPipeline.return_value
            mock_instance.run_pipeline.return_value = "<table><tr><td>fake result</td></tr></table>"

            response = client.post(
                "/predict",
                files={"file": ("test.csv", fake_file, "text/csv")},
            )

            assert response.status_code == 200
            assert "fake result" in response.text
            mock_instance.run_pipeline.assert_called_once()

    def test_predict_failure_raises_network_security_exception(self):
        fake_file = io.BytesIO(b"col1,col2\n1,2\n3,4")

        with patch(
            "src.NetworkSecurity.pipeline.batch_predictions.BatchPredictionPipeline"
        ) as MockBatchPipeline, \
             patch("app.TrainingPipelineConfig"):

            MockBatchPipeline.return_value.run_pipeline.side_effect = Exception("prediction blew up")

            response = client.post(
                "/predict",
                files={"file": ("test.csv", fake_file, "text/csv")},
            )

            assert response.status_code == 500

    def test_predict_without_file_returns_422(self):
        # FastAPI should reject the request before it ever reaches the route body
        response = client.post("/predict")

        assert response.status_code == 422