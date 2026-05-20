
## Structure

```text
cloud-native-react-fastapi-template/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── config.py
│       ├── database.py
│       ├── main.py
│       └── test_main.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration DB

Copier le fichier d'exemple :

```bash
cp .env.example .env
```

Variables disponibles :

```env
DB_ENABLED=true
DB_TYPE=sqlite
SQLITE_PATH=./app.db
DB_HOST=db
DB_PORT=5432
DB_NAME=app_db
DB_USER=postgres
DB_PASSWORD=postgres
```

### Mode SQLite par défaut

Aucune base externe n'est nécessaire.

```env
DB_ENABLED=true
DB_TYPE=sqlite
SQLITE_PATH=./app.db
```

Lancer le projet :

```bash
docker compose up --build
```

### Mode sans base de données

```env
DB_ENABLED=false
```

### Mode PostgreSQL avec Docker

```env
DB_ENABLED=true
DB_TYPE=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=app_db
DB_USER=postgres
DB_PASSWORD=postgres
```

Lancer avec le service PostgreSQL :

```bash
docker compose --profile postgres up --build
```

## URLs

- Frontend : http://localhost:3001
- Backend : http://localhost:8081
- Statut DB : http://localhost:8081/api/db/status

## Lancement sans Docker

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest
```
