# Dockerfile pour Hugging Face Space (Docker runtime)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Installer d'abord les deps Python (cache de layer)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . /app

# (Optionnel) Non-root user
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH

EXPOSE ${PORT}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1", "--proxy-headers"]
