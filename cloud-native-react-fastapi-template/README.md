

##  Structure du Projet
```text
cloud-native-react-fastapi-template/
├── README.md           
├── docker-compose.yml  
├── .gitignore          
├── frontend/           
│   ├── Dockerfile
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/            
└── backend/            
    ├── Dockerfile
    ├── requirements.txt
    └── app/            
```


##  Lancement avec Docker

1. docker-compose up --build
3. Accédez à l'application :
   - **Frontend** : [http://localhost:3001](http://localhost:3001)
   - **Backend API** : [http://localhost:8080/api/hello](http://localhost:8080/api/hello)

## Lancement sans Docker

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python app/main.py` (ou `uvicorn app.main:app --reload`)

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

