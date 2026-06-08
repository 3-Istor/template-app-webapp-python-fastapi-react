# vfcnpdemoapp — RoomPulse Store

A clean demo ecommerce app built with FastAPI, React, PostgreSQL, Docker Compose, and Docker secrets.

The store sells **RoomPulse**, an IoT device for smart meeting rooms. The demo shows a real checkout flow: React sends a secret-protected order request to FastAPI, FastAPI validates the Docker secret, then saves the order and updates stock in PostgreSQL.

## Services shown

- **Frontend:** React + Vite storefront on port `3001`
- **Backend:** FastAPI API on port `8081`
- **Database:** PostgreSQL 16 in Docker
- **Secrets:** Docker Compose secrets sourced from `.env`

## Environment files

`.env` contains local demo values and is used by Docker Compose.

`.env.example` contains the same keys with safe placeholder values.

Important keys:

```env
API_SECRET_KEY=dev-local-secret-change-me
VITE_DEMO_SECRET=dev-local-secret-change-me
POSTGRES_PASSWORD=roompulse_password
```

`API_SECRET_KEY` is mounted into the backend as a Docker secret.

`POSTGRES_PASSWORD` is mounted into PostgreSQL and the backend as a Docker secret.

`VITE_DEMO_SECRET` is injected into the React app so the checkout form starts with the correct demo secret.

## Run

```bash
docker compose down -v
docker compose up --build
```

Open:

- Frontend: http://localhost:3001
- Backend: http://localhost:8081/api/status

## Demo flow

1. Open the storefront.
2. Check the service panel: PostgreSQL should show connected and Docker secret should show loaded.
3. Place an order using the prefilled demo secret.
4. The order is saved in PostgreSQL and appears in recent orders.
5. Product stock decreases after checkout.
