from dataclasses import dataclass

@dataclass
class DataIngestionArtifactConfig:
    train_file_path: str
    test_file_path: str