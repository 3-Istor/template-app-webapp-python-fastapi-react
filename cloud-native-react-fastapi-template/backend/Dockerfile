# Utilise Python 3.11 slim pour une image légère
FROM python:3.11-slim

# Définit le dossier de travail
WORKDIR /app

# Copie les dépendances et les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY . .

# Expose le port 8000
EXPOSE 8000

# Commande pour lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
