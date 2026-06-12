# Template FastAPI + React

Template de démarrage pour une application web moderne basée sur FastAPI côté backend et React + Vite côté frontend.

Le backend est actuellement volontairement minimaliste pour servir de base propre à des évolutions futures. Il utilise :

- Python 3.11 dans l’image Docker du backend
- FastAPI 0.104.1
- Uvicorn pour le serveur ASGI
- SQLAlchemy 2.x pour la couche d’accès aux données
- Pydantic Settings pour la configuration par variables d’environnement

## Installation & Démarrage

### Prérequis

- Python 3.11 ou supérieur
- Node.js 18+ si vous démarrez aussi le frontend
- pip et virtualenv/venv

### Backend en local

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend en local

```bash
cd frontend
npm install
npm run dev
```

### Démarrage avec Docker

```bash
docker compose up --build
```

Le backend est exposé sur http://localhost:8081 et le frontend sur http://localhost:3001.

### Base de données

La configuration est pilotée par variables d’environnement. Le backend accepte trois modes :

- `DB_ENABLED=true` et `DB_TYPE=sqlite` pour un mode local sans dépendance externe
- `DB_ENABLED=true` et `DB_TYPE=postgres` pour PostgreSQL
- `DB_ENABLED=false` pour désactiver toute connexion à la base

Exemple minimal pour SQLite :

```env
DB_ENABLED=true
DB_TYPE=sqlite
SQLITE_PATH=./app.db
```

Pour PostgreSQL avec Docker, activez le profil dédié :

```bash
docker compose --profile postgres up --build
```

## Structure du projet

Structure actuelle du dépôt :

```text
template-app-webapp-python-fastapi-react/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       ├── main.py
│       └── test_main.py
├── deploy/
│   ├── values-backend.yaml
│   └── values-frontend.yaml
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── style.css
├── docker-compose.yml
└── README.md
```

Structure cible recommandée pour faire évoluer le backend sans casser l’architecture :

```text
backend/app/
├── core/
│   └── config.py
├── database/
│   ├── base.py
│   └── session.py
├── models/
├── schemas/
├── routers/
├── services/
└── main.py
```

Règle pratique : les routes restent fines, les validations vivent dans les schémas Pydantic, et la logique métier doit sortir du router dès qu’elle devient non triviale.

## Documentation interactive

Une fois le backend démarré, ouvrez :

- http://localhost:8000/docs pour Swagger UI
- http://localhost:8000/redoc pour ReDoc

Si vous passez par Docker Compose, l’API reste accessible via http://localhost:8081/docs et http://localhost:8081/redoc.

## Tests

```bash
cd backend
pytest
```

## 🤖 Tu travailles avec une IA ?

Oui. Un fichier de contexte dédié existe pour guider un LLM ou un assistant de code : [ai-context.md](ai-context.md).

Ce fichier explique comment ajouter une route, une entité, des schémas, des dépendances ou des validations sans casser les conventions du template. Si vous modifiez le backend avec une IA, faites lire ce fichier en premier.
