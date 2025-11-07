import os
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

INTENTS_PATH = "intents.json"

# 🧠 Función auxiliar
def cargar_intents():
    if os.path.exists(INTENTS_PATH):
        with open(INTENTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("intents", [])
    return []

def guardar_intents(intents):
    with open(INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"intents": intents}, f, indent=2, ensure_ascii=False)


# 🏠 Ruta principal (Home)
@app.route("/", methods=["GET", "POST"])
def home():
    intents = cargar_intents()

    if request.method == "POST":
        tag = request.form.get("tag")
        patterns = request.form.get("patterns")
        responses = request.form.get("responses")

        if tag and patterns and responses:
            intents.append({
                "tag": tag,
                "patterns": [patterns],
                "responses": [responses]
            })
            guardar_intents(intents)
        return render_template("home.html", intents=intents)

    return render_template("home.html", intents=intents)


# 🔁 Actualizar intent
@app.route("/actualizar", methods=["POST"])
def actualizar():
    intents = cargar_intents()
    oldtag = request.form.get("oldtag")
    newtag = request.form.get("newtag")
    newpatterns = request.form.get("newpatterns")
    newresponses = request.form.get("newresponses")

    for intent in intents:
        if intent["tag"] == oldtag:
            intent["tag"] = newtag
            intent["patterns"] = [newpatterns]
            intent["responses"] = [newresponses]
            break

    guardar_intents(intents)
    return render_template("home.html", intents=intents)


# 🗑️ Eliminar intent
@app.route("/eliminar", methods=["POST"])
def eliminar():
    intents = cargar_intents()
    tag = request.form.get("tag")
    intents = [i for i in intents if i["tag"] != tag]
    guardar_intents(intents)
    return render_template("home.html", intents=intents)


# 🚀 Entrenar modelo (simulado)
@app.route("/train", methods=["GET", "POST"])
def train():
    print("Entrenando modelo...")
    return jsonify({"status": "Modelo entrenado con éxito"})


# 🔄 Resetear y entrenar (simulado)
@app.route("/resetandtrain", methods=["GET", "POST"])
def resetandtrain():
    print("Reseteando y reentrenando modelo...")
    return jsonify({"status": "Modelo reseteado y entrenado"})


# 💬 Ruta para el chat
@app.route("/chat")
def chat():
    return render_template("chat4.html")


# 🧠 Predicción simple (por ahora simulada)
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    pregunta = data.get("mensaje", "").lower()
    if not pregunta:
        return jsonify({"respuesta": "Hola"})
    return jsonify({"respuesta": "Hola desde el backend Flask!"})


# 🧩 SocketIO
@socketio.on("message")
def handle_message(msg):
    print("Mensaje recibido:", msg)
    socketio.send(f"Echo: {msg}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
