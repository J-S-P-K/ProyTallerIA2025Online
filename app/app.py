import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

# Crear la app Flask
app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------------------
# RUTAS PRINCIPALES
# ---------------------------

# Home (interfaz de backend)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Ejemplo: guardar nuevas preguntas y respuestas
        tag = request.form.get("tag")
        patterns = request.form.get("patterns")
        responses = request.form.get("responses")
        print(f"Nueva entrada: {tag}, {patterns}, {responses}")
        # Aquí podrías guardar en intents.json o base de datos
    return render_template("home.html", intents=[])

# Ruta para chat
@app.route("/chat")
def chat():
    return render_template("chat4.html")

# Entrenar modelo
@app.route("/train", methods=["GET"])
def train():
    print("Entrenando modelo...")
    # Aquí podrías cargar y entrenar el modelo real
    return jsonify({"status": "Modelo entrenado con éxito"})

# Resetear y entrenar
@app.route("/resetandtrain", methods=["GET"])
def reset_and_train():
    print("Reseteando y entrenando modelo...")
    # Lógica real de reset + entrenamiento
    return jsonify({"status": "Modelo reseteado y entrenado con éxito"})

# Endpoint de predicción
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    msg = data.get("mensaje", "")
    respuesta = f"Echo desde backend: {msg}"
    return jsonify({"respuesta": respuesta})

# ---------------------------
# SOCKET.IO EVENTOS
# ---------------------------
@socketio.on("message")
def handle_message(msg):
    print(f"Mensaje recibido: {msg}")
    socketio.send(f"Echo: {msg}")

# ---------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
