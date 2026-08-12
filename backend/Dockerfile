# Imagen base oficial de Python slim para mantener el contenedor liviano
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero solo requirements para aprovechar el cache de Docker.
# Si el código cambia pero las dependencias no, Docker no reinstala todo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Puerto en el que escucha uvicorn (Railway asigna el puerto via variable PORT)
EXPOSE 8000

# Comando de inicio: usa la variable PORT de Railway si existe, sino 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
