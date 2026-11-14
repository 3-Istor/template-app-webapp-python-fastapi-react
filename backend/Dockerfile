FROM python:3.14-slim

WORKDIR /app

# Debian security fixes reach the base image days after they ship.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# pip is unused at runtime and its vendored dependencies carry CVEs: add
# packages to requirements.txt and rebuild instead.
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y pip \
    && chown 1000:1000 /app

COPY --chown=1000:1000 . .

# 1000 matches the usual host uid, so the docker-compose bind mount stays
# writable for the SQLite fallback.
USER 1000:1000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
