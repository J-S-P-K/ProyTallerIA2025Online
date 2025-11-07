# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render detecta este puerto
EXPOSE 5000

# Variable de entorno para Flask
ENV PORT=5000
ENV FLASK_ENV=production

CMD ["python", "app.py"]

