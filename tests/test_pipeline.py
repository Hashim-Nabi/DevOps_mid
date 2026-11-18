"""Pipeline tests - run inside the freshly built image (artifacts already trained)."""
import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import app as service
from train import fit_reference

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text())
MIN_ACCURACY = 0.60


def test_dataset_is_valid():
    df = pd.read_csv(ROOT / "dataset" / "train.csv")
    assert len(df) >= 100
    assert set(CONFIG["features"] + ["label"]).issubset(df.columns)
    assert df["label"].nunique() == 2


def test_model_accuracy_is_acceptable():
    df = pd.read_csv(ROOT / "dataset" / "train.csv")
    _, accuracy = fit_reference(df, CONFIG)
    assert accuracy >= MIN_ACCURACY, f"accuracy {accuracy:.3f} below {MIN_ACCURACY}"


def test_metrics_file_matches_dataset():
    m = json.loads((ROOT / "artifacts" / "metrics.json").read_text())
    df = pd.read_csv(ROOT / "dataset" / "train.csv")
    assert m["student_id"] == CONFIG["student_id"] == "FA23-BDS-057"
    assert m["training_rows"] == len(df)
    assert m["accuracy"] >= MIN_ACCURACY


def test_metrics_endpoint_fields():
    r = TestClient(service.app).get("/metrics")
    assert r.status_code == 200
    body = r.json()
    for key in ("student_id", "accuracy", "training_rows", "model_version", "git_sha"):
        assert key in body


def test_predict_endpoint():
    rec = {f: 0.0 for f in CONFIG["features"]}
    r = TestClient(service.app).post("/predict", json={"records": [rec, rec]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["predictions"]) == 2
    assert all(p in (0, 1) for p in body["predictions"])
