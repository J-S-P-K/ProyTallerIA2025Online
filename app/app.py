import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

# Crear la app Flask
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Ruta raíz (para verificar que el servidor funcione)
@app.route('/')
def home():
    return "Servidor Flask corriendo correctamente ✅. Rutas disponibles: /chat y /train"

# Ruta para el chat (frontend)
@app.route('/chat')
def chat():
    return render_template('chat4.html')

# Ruta para entrenar el modelo (backend)
@app.route('/train', methods=['POST'])
def train():
    data = request.json
    # Aquí podés agregar tu lógica de entrenamiento o cargar el modelo
    # Ejemplo:
    print("Entrenando modelo con:", data)
    return jsonify({"status": "Modelo entrenado con éxito"})

# Ejemplo de endpoint para predicción
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # Acá iría tu lógica de predicción real
    return jsonify({"respuesta": "Hola desde el backend Flask!"})

# Eventos SocketIO
@socketio.on('message')
def handle_message(msg):
    print('Mensaje recibido:', msg)
    socketio.send(f"Echo: {msg}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
