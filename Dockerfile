# ML retraining service - FA23-BDS-057
# The model is trained while the image is built, so every image contains the
# model for exactly one dataset version and one git commit.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Jenkins passes the commit being built; train.py records it as git_sha
ARG GIT_COMMIT=local
ENV GIT_COMMIT=${GIT_COMMIT}
RUN python train.py

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
