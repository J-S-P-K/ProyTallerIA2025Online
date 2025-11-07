from flask import Flask
from flask import request, render_template, redirect, session, copy_current_request_context
from flask_cors import CORS, cross_origin
from flask import jsonify
from threading import Lock
import os
import sys
import json
from flask_sqlalchemy import SQLAlchemy

# comprobar / descargar punkt solo si hace falta
try:
    import nltk
    nltk.data.find("tokenizers/punkt")
except Exception:
    import nltk
    nltk.download("punkt")

from static.nltk_utils import bag_of_words, tokenize
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# -----------------------
# APP / SOCKETIO / CORS
# -----------------------
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
cors = CORS(app)

# -----------------------
# Database (SQLite) — ruta segura cross-platform
# -----------------------
project_dir = os.path.dirname(os.path.abspath(__file__))
# ruta al archivo intents.db dentro de la carpeta static
db_path = os.path.join(project_dir, 'static', 'intents.db')
# Aseguramos que la carpeta exista
os.makedirs(os.path.dirname(db_path), exist_ok=True)
# SQLAlchemy wants a URI; use absolute path and forward slashes
db_uri = "sqlite:///{}".format(os.path.abspath(db_path).replace("\\", "/"))
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# create tables if they don't exist (safe)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        # log para debugging en deploy
        print("Warning: create_all() error:", e)

app.config['CORS_HEADERS'] = 'Content-Type'

# -----------------------
# Importar funciones de entrenamiento (si existen)
# -----------------------
# Intento importar trainf y trainf2; si faltan, exponemos un stub que no rompe
try:
    from static.train3 import trainf
except Exception as e:
    def trainf():
        print("trainf() not available:", e)

try:
    from static.train2 import trainf2
except Exception as e:
    def trainf2():
        print("trainf2() not available:", e)

# -----------------------
# MODELO DB ORM (igual que tu original)
# -----------------------
class Intents(db.Model):
    intents_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    tag = db.Column(db.String(60), nullable=False)
    patterns = db.Column(db.String(60), nullable=False)
    responses = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return "<id: {}>".format(self.intents_id)

# -----------------------
# RUTAS (home, train, reset, chat, CRUD)
# -----------------------
@app.route("/", methods=["GET", "POST"])
@cross_origin()
def home():
    intents = None
    if request.method == "POST" and request.form:
        try:
            inte = Intents(tag=request.form.get("tag"),
                           patterns=request.form.get("patterns"),
                           responses=request.form.get("responses"))
            db.session.add(inte)
            db.session.commit()
            print("Agregado exitosamente:", inte)
        except Exception as e:
            print("Error al agregar un intent:", e)
    # consultar la DB (devuelve lista de Intents)
    try:
        intents = Intents.query.all()
    except Exception as e:
        print("Error al leer intents desde DB:", e)
        intents = []
    return render_template("home.html", intents=intents)

@app.route("/actualizar", methods=["POST"])
@cross_origin()
def update():
    try:
        newtag = request.form.get("newtag")
        oldtag = request.form.get("oldtag")
        newpatterns = request.form.get("newpatterns")
        newresponses = request.form.get("newresponses")
        intent = Intents.query.filter_by(tag=oldtag).first()
        if intent:
            intent.tag = newtag
            intent.patterns = newpatterns
            intent.responses = newresponses
            db.session.commit()
            print("Actualizado intent:", oldtag, "->", newtag)
        else:
            print("Intent a actualizar no encontrado:", oldtag)
    except Exception as e:
        print("No se pudo actualizar el intent:", e)
    return redirect("/")

@app.route("/eliminar", methods=["POST"])
@cross_origin()
def delete():
    try:
        tag = request.form.get("tag")
        intent = Intents.query.filter_by(tag=tag).first()
        if intent:
            db.session.delete(intent)
            db.session.commit()
            print("Eliminado intent:", tag)
        else:
            print("Intent a eliminar no encontrado:", tag)
    except Exception as e:
        print("Error al eliminar intent:", e)
    return redirect("/")

# Rutas de entrenamiento — usamos GET por compatibilidad con tus botones
@app.route('/train', methods=['GET'])
def route_train():
    try:
        trainf()
    except Exception as e:
        print("trainf() error:", e)
    return jsonify({"status": "train_called"})

@app.route('/resetandtrain', methods=['GET'])
def route_reset_train():
    try:
        trainf2()
    except Exception as e:
        print("trainf2() error:", e)
    return jsonify({"status": "reset_and_train_called"})

# Rutas auxiliares que tu proyecto usa
@app.route('/backend')
@cross_origin()
def projects():
    return render_template("index.html", title='Frontend') if os.path.exists(os.path.join(project_dir, 'templates', 'index.html')) else ("", 204)

# Mantener /chat tal cual
@app.route('/chat')
@cross_origin()
def newchat():
    return render_template("chat4.html")

# -----------------------
# Integracion con tu antiguo getRespuestaIA
# -----------------------
from static.chat3 import getRespuestaIA
def getRespuestaApi(message):
    respuesta = 'No entiendo la pregunta...'
    try:
        respuesta = getRespuestaIA(message)
    except Exception as e:
        print("Error en getRespuestaIA:", e)
    return respuesta

# -----------------------
# SocketIO events: mantener nombres y comportamiento
# -----------------------
@socketio.event
def my_event(message):
    # si el cliente envía el mensaje de conexión, respondemos 'Estoy conectado!'
    try:
        if str(message.get('data')) == "I\\'m connected!" or str(message.get('data')) == "I'm connected!":
            emit('my_response', {'data': 'Estoy conectado!'})
            return
    except Exception:
        pass

    # usar modelo
    try:
        resp = getRespuestaApi(message.get('data'))
    except Exception as e:
        print("Error al obtener respuesta IA:", e)
        resp = "hola"  # fallback mínimo
    emit('my_response', {'data': resp})

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    try:
        session['receive_count'] = session.get('receive_count', 0) + 1
    except Exception:
        pass
    emit('my_response', {'data': 'Disconnected!'}, callback=can_disconnect)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

# -----------------------
# Ejecutar con socketio (0.0.0.0 y puerto desde env)
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    # IMPORTANT: usar socketio.run para SocketIO; allow_unsafe_werkzeug para entornos tipo Render
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
