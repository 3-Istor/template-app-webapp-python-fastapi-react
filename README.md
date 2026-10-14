# template-app-webapp-python-fastapi-react

## Rôle

Modèle de dépôt applicatif fullstack : backend FastAPI et frontend React/Vite, configurations locales, conteneurs et valeurs de déploiement distinctes pour les deux composants.

## Technologies

Python, FastAPI, Uvicorn, SQLAlchemy et Pydantic Settings ; JavaScript/JSX, React 19, Vite, Docker/Compose, YAML Helm et GitHub Actions. Les Dockerfiles utilisent Python 3.14 et Node.js 26.

## Entrées

| Origine / destinataire | Contenu et transmission |
| --- | --- |
| CMP / app-templates | Sélection comme template GitHub ; lors du provisioning, `k3s-gitops-app` écrit les valeurs du projet dans la copie créée. |
| Développeurs / environnement applicatif | Code métier, variables d’environnement et base SQLite/PostgreSQL facultative. |

## Sorties et consommateurs

| Origine / destinataire | Contenu et transmission |
| --- | --- |
| Dépôts applicatifs / développeurs | Sources backend/frontend, Dockerfiles, CI et configurations copiés par GitHub lors de la création du dépôt. |
| GHCR / cluster cible | Deux images, `<owner>/<repo>/frontend` et `<owner>/<repo>/backend`, construites par la CI du dépôt. |
| K3s / Argo CD / infra-templates | `deploy/values-frontend.yaml` et `deploy/values-backend.yaml` de la copie applicative, utilisés pour rendre le chart générique. |

## Documentation CNP

[Fiche `template-app-webapp-python-fastapi-react` et workflows inter-repo](https://github.com/3-Istor/cnp-docs/blob/main/docs/04-templates/00-github-repositories-landscape.md#template-app-webapp-python-fastapi-react).

## Installation & Démarrage

### Prérequis

- Python 3.11 ou supérieur
- Node.js compatible avec la version de Vite du `frontend/package.json` (le Dockerfile utilise Node.js 26)
- pip et virtualenv/venv

### Backend en local

```bash
cd backend
python3 -m venv .venv
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

### Migrations de base de données

Le schéma est géré par [Alembic](https://alembic.sqlalchemy.org/), selon le standard de migration CNP v1. `docker compose up` applique les migrations avant de démarrer le backend, comme la plateforme le fait avant chaque release.

| Règle | Concrètement |
|---|---|
| M-1 | Les migrations sont des fichiers versionnés dans `backend/migrations/versions/`. |
| M-2 | Aucune modification de schéma au démarrage : pas de `Base.metadata.create_all()`. |
| M-3 | Un seul point d'entrée, `backend/migrate`, idempotent : relancé sans rien à faire, il sort en 0. |
| M-4 | En prod, seule la plateforme lance les migrations, dans un Job exécuté après une sauvegarde de la base. |
| M-5 | **Toute migration de la release N fonctionne avec le code de la release N-1**, qui tourne encore pendant le déploiement. |
| M-6 | Pas de migration descendante en prod : on corrige avec une nouvelle migration. |
| M-7 | Pas de traitement de données lourd dans une migration (limite de 4 min). Les backfills se font dans le code, par lots. |

Ce qui passe en une release et ce qui se découpe :

| Opération | Releases | Comment |
|---|---|---|
| Ajouter une table, une colonne nullable ou avec défaut | 1 | Direct. |
| Ajouter un index | 1 | `postgresql_concurrently=True` dans `op.get_context().autocommit_block()`. |
| Rendre une colonne obligatoire | 2 | N : le code écrit toujours la valeur, backfill. N+1 : `nullable=False`. |
| Supprimer une colonne ou une table | 2 | N : le code ne la lit plus. N+1 : `drop_column`. |
| Renommer ou changer le type d'une colonne | 3 | N : nouvelle colonne, écriture dans les deux, backfill. N+1 : lecture de la nouvelle. N+2 : suppression de l'ancienne. |

Au quotidien :

1. Modifier les modèles dans `backend/app/models.py`.
2. `make migration name="add email_verified"` génère la révision avec `alembic revision --autogenerate`.
3. Relire le fichier généré. L'autogenerate prend un renommage pour une suppression suivie d'un ajout.
4. `docker compose up` applique la migration en local.
5. Ouvrir la PR. La CI vérifie la règle M-5 avec [squawk](https://squawkhq.com/) sur le SQL PostgreSQL de chaque nouvelle révision.

La révision qui termine un découpage, par exemple le `drop_column` de la release N+1, le déclare dans son fichier : `squawk_ignore = ["ban-drop-column"]`. Une migration qui casse vraiment la version en cours demande le label de PR `migration:breaking`, puis la validation d'un admin du projet au moment de la release.

Pour lancer une release, poser un tag `vX.Y.Z` sur main. La CI publie les images avec le tag `X.Y.Z`.

## Structure du projet

Structure actuelle du dépôt :

```text
template-app-webapp-python-fastapi-react/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── migrate                   # point d'entrée des migrations
│   ├── .squawk.toml              # règles du lint de migration
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   ├── scripts/
│   │   └── lint_migrations.py
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── main.py
│       ├── test_main.py
│       └── test_migrations.py
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
├── Makefile
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
