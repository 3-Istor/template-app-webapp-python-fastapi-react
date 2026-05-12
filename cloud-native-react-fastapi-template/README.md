# cloud-native-react-fastapi-template

Une template complète et professionnelle pour une application web Cloud Native utilisant **React (Vite)** et **FastAPI (Python)**, entièrement containerisée avec **Docker**.

## 🚀 Objectif
Ce repository sert de point de départ pour des applications web modernes. Il inclut un frontend React communiquant avec un backend FastAPI, le tout orchestré par Docker Compose.

## 📁 Structure du Projet
```text
cloud-native-react-fastapi-template/
├── README.md           # Documentation
├── docker-compose.yml  # Orchestration Docker
├── .gitignore          # Fichiers ignorés par Git
├── frontend/           # Application React (Vite)
│   ├── Dockerfile
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/            # Code source React
└── backend/            # API FastAPI (Python)
    ├── Dockerfile
    ├── requirements.txt
    └── app/            # Code source Python
```

## 🛠️ Prérequis
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- (Optionnel) Node.js & Python 3.11 pour le développement local sans Docker

## 🐳 Lancement avec Docker (Recommandé)

1. Clonez le repository.
2. À la racine du projet, lancez :
   ```bash
   docker-compose up --build
   ```
3. Accédez à l'application :
   - **Frontend** : [http://localhost:3001](http://localhost:3001)
   - **Backend API** : [http://localhost:8080/api/hello](http://localhost:8080/api/hello)

## 💻 Lancement sans Docker

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python app/main.py` (ou `uvicorn app.main:app --reload`)

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## 🔗 URLs Utiles
- Frontend : `http://localhost:3001`
- Backend API : `http://localhost:8080/api/hello`
- Documentation API (Swagger) : `http://localhost:8080/docs`

## 📝 Explications
- **Frontend** : Développé en React avec Vite pour une rapidité optimale. Il appelle l'API backend au chargement de la page.
- **Backend** : API performante avec FastAPI. Gère les requêtes et les CORS pour permettre au frontend de communiquer.
- **Docker** : Permet de garantir que l'application fonctionne de la même manière sur toutes les machines.
