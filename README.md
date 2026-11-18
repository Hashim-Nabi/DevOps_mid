# CSC418 Lab Midterm - Automated ML Retraining Pipeline

Student: Hashim Nabi Sulehria - **FA23-BDS-057** (scenario `smart_water`, seed 32023)

GitHub push -> webhook -> Jenkins job `MIDTERM-FA23-BDS-057` -> train.py + tests -> Docker image -> redeploy on EC2 -> e-mail.

| File | Purpose |
|---|---|
| `config.json` | Individual configuration (from the instructor repo) |
| `generate_dataset.py`, `train.py`, `app.py` | Supplied starter code (unchanged) |
| `dataset/train.csv` | Generated with `python generate_dataset.py` (300 rows) |
| `Dockerfile` | Installs deps, runs `train.py` at build time, serves FastAPI on 8000 |
| `Jenkinsfile` | Fetch data -> build (train) -> test -> deploy -> e-mail |
| `tests/test_pipeline.py` | pytest checks (dataset, accuracy, /metrics, /predict) |
| `scripts/notify.py` | Post-build e-mail via SMTP |

API (port 8000): `GET /metrics`, `POST /predict`, `GET /health`.


