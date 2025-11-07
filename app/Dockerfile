# syntax=docker/dockerfile:1
FROM python:3.10.11

WORKDIR /docs

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Instalar dependencias
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Render expone automáticamente el puerto $PORT (usualmente 10000)
# por eso se recomienda hacer esto:
EXPOSE 10000

# Copiar todo el código
COPY . .

# Ejecutar el servidor Flask con SocketIO
CMD ["python", "app.py"]
