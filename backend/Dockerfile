FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && chown 1000:1000 /app

COPY --chown=1000:1000 . .

# 1000 matches the usual host uid, so the docker-compose bind mount stays
# writable for the SQLite fallback.
USER 1000:1000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
