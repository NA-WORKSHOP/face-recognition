# Minimal CPU-only InsightFace Flask app
# Use Amazon ECR Public mirror for Docker Official Images to avoid Hub DNS issues
FROM public.ecr.aws/docker/library/python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    INSIGHTFACE_HOME=/root/.insightface \
    PORT=8000

WORKDIR /app

# System deps for opencv headless and runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
