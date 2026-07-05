# Network Security — Phishing URL Detection - MLOps

An end-to-end machine learning system that detects phishing websites from URL-based features. The project covers the full MLOps lifecycle: data ingestion from MongoDB, automated validation and drift detection, feature transformation, model training with experiment tracking, a REST API for training/inference, and containerized deployment.

---

## Overview

Phishing websites are typically identified by a set of structural and behavioral URL characteristics (e.g. use of IP addresses, URL length, SSL state, domain age, etc.). This project builds a classification pipeline that ingests labeled phishing/legitimate URL data, validates and transforms it, trains multiple candidate models, and serves the best-performing model through a FastAPI web service with every stage automated, logged, versioned, and reproducible.

---

## Architecture

**Pipeline flow:**

```
MongoDB Atlas  →  Data Ingestion  →  Data Validation  →  Data Transformation  →  Model Training  →  final_model/
```

The trained model and preprocessor produced by the pipeline are then served through a FastAPI application, which is containerized and deployed via CI/CD:

```
final_model/  →  FastAPI Service (/train, /predict)  →  Docker Image  →  DockerHub
```

**What each stage does:**

| # | Stage | Input | Output |
|---|---|---|---|
| 1 | **Data Ingestion** | MongoDB collection | Feature-store CSV + train/test split |
| 2 | **Data Validation** | Train/test CSVs | Schema check + KS-test drift report (YAML) |
| 3 | **Data Transformation** | Validated train/test data | Fitted KNN-imputer preprocessor + transformed arrays |
| 4 | **Model Training** | Transformed arrays | Best-performing model, logged to MLflow via DagsHub |
| 5 | **Serving** | `final_model/` (model + preprocessor) | FastAPI endpoints for retraining and batch inference |
| 6 | **Deployment** | Docker image | Built and pushed to DockerHub via GitHub Actions |

---

## Tech Stack

**Language & Core Libraries**
- Python 3.10
- Pandas, NumPy
- scikit-learn (`RandomForestClassifier`, `DecisionTreeClassifier`, `GradientBoostingClassifier`, `LogisticRegression`, `AdaBoostClassifier`, `KNNImputer`)
- SciPy (Kolmogorov–Smirnov test for data drift detection)

**Data & Storage**
- MongoDB Atlas (raw dataset storage via `pymongo`)
- YAML-based schema configuration and drift reporting

**ML Experiment Tracking**
- MLflow
- DagsHub (remote MLflow tracking server)

**API & Serving**
- FastAPI
- Uvicorn (ASGI server)
- Jinja2 (HTML result rendering for batch predictions)
- python-multipart (file upload support)

**Testing**
- Pytest
- FastAPI `TestClient` / `httpx`
- `unittest.mock` for isolating pipeline stages in tests

**DevOps & Infrastructure**
- Docker (containerized deployment)
- GitHub Actions (CI/CD — automated testing, multi-arch image build & push to DockerHub)

---

## Pipeline Components

| Stage | Responsibility |
|---|---|
| **Data Ingestion** | Pulls raw records from a MongoDB collection, exports a feature-store CSV snapshot, and performs a train/test split. |
| **Data Validation** | Verifies the ingested data matches an expected schema and runs statistical drift detection (KS-test) between train and test distributions, producing a drift report. |
| **Data Transformation** | Applies a `scikit-learn` `Pipeline` with `KNNImputer` to handle missing values, and serializes the fitted preprocessor for reuse at inference time. |
| **Model Training** | Trains and hyperparameter-tunes several classifiers, selects the best performer by evaluation score, logs metrics/artifacts to MLflow (via DagsHub), and exports the final model + preprocessor. |

Each stage communicates through typed **artifact** and **config** entities, keeping the pipeline modular and independently testable.

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Redirects to interactive API docs (`/docs`) |
| `GET` | `/train` | Triggers the full training pipeline end-to-end |
| `POST` | `/predict` | Accepts a CSV file upload, runs batch inference using the saved model, and returns results as an HTML table |


---

## Running Locally

```bash
# Clone and install dependencies
git clone <repo-url>
cd NetworkSecurity
pip install -r requirements.txt

# Set required environment variables (.env)
MONGO_DB_URL=<your-mongodb-connection-string>

# Run the training pipeline directly
python main.py

# Or launch the API
python app.py
# → visit http://localhost:8000/docs
```

## Running with Docker

```bash
docker build -t networksecurity .
docker run -p 8000:8000 --env-file .env networksecurity
```

## Testing

```bash
pytest tests/ -v
```

Unit tests mock external dependencies (MongoDB, model training, file I/O) to validate pipeline orchestration logic and API behavior in isolation.

## CI/CD

GitHub Actions automates:
1. **Continuous Integration** — dependency installation and automated test execution on every push.
2. **Continuous Delivery** — multi-architecture Docker image build (amd64/arm64) and push to DockerHub.

---

## License

This project is for educational purposes.