## Dockerfile for Hugging Face Space (Docker runtime)
## Runs a FastAPI app with uvicorn on port 7860.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Workdir
WORKDIR /app

# System deps (keep minimal). Add build tools for wheels if needed.
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential \
         curl \
         git \
         git-lfs \
     && rm -rf /var/lib/apt/lists/* \
     && git lfs install


# Install Python deps first for better layer caching
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Create a non-root user and fix permissions (do this after installing packages)
RUN useradd -m -u 1000 user \
    && chown -R user:user /app

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH


# Hugging Face Spaces expect port 7860
EXPOSE ${PORT}

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1", "--proxy-headers"]
