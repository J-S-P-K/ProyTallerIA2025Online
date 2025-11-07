from flask import Flask
from flask import request,render_template,redirect,session, copy_current_request_context
from flask_cors import CORS, cross_origin
from flask import jsonify
from threading import Lock
import os
import sys
import json
from flask_sqlalchemy import SQLAlchemy

from static.nltk_utils import bag_of_words, tokenize
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
cors = CORS(app)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir+'\\static', "intents.db"))
#print(database_file)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.config['CORS_HEADERS'] = 'Content-Type'

port = int(os.environ.get("PORT", 10000))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)

""" @app.route('/')
@cross_origin()
def index():
    return  """"<p><a href=""/chat"">Chat</a></p> <p><a href=""/backend"">Backend</a></p>"
from static.train3 import trainf


@app.route('/train',methods=['GET'])
def train():
    trainf()
    return "<p> Get Train! </p>"

from static.train2 import trainf2
@app.route('/resetandtrain',methods=['GET'])
def train2():
    trainf2()
    return "<p> Get Train! </p>"

@app.route('/backend')
@cross_origin()
def projects():
    return render_template("index.html", title = 'Frontend')

from static.chat2 import chaty
@app.route('/chat2')
@cross_origin()
def chat2():
    chaty()
    return "<p> Get Chat!</p>"


@app.route('/chat')
@cross_origin()
def newchat():
    return render_template("chat4.html")



class Intents(db.Model):
    intents_id= db.Column(db.Integer, autoincrement=True,primary_key=True,unique=True, nullable=False)
    tag= db.Column(db.String(60), nullable=False)
    patterns= db.Column(db.String(60), nullable=False)
    responses= db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return "<id: {}>".format(self.intents_id)

@app.route("/", methods=["GET", "POST"])
@cross_origin()
def home():
    intents = None
    if request.form:
        try:
            inte= Intents(tag=request.form.get("tag"),patterns=request.form.get("patterns"),responses=request.form.get("responses"))
            db.session.add(inte)
            db.session.commit()
        except Exception as e:
            print("Error al agregar un intent")
            print(e)
        finally:
            print("Agregado exitosamante!")
    intents = Intents.query.all()
    return render_template("home.html", intents=intents)

@app.route("/actualizar", methods=["POST"])
@cross_origin()
def update():
    try:
        newtag = request.form.get("newtag")
        oldtag = request.form.get("oldtag")
        newpatterns=request.form.get("newpatterns")
        #oldpatterns=request.form.get("oldpatterns")
        newresponses=request.form.get("newresponses")
        #oldresponses=request.form.get("oldresponses")
        intent= Intents.query.filter_by(tag=oldtag).first()
        intent.tag = newtag
        intent.patterns= newpatterns
        intent.responses=newresponses
        db.session.commit()
    except Exception as e:
        print("No se pudo actualizar el intent")
        print(e)
    finally:
        print("Actualizado!")
    
    return redirect("/")


@app.route("/eliminar", methods=["POST"])
@cross_origin()
def delete():
    tag = request.form.get("tag")
    intent = Intents.query.filter_by(tag=tag).first()
    db.session.delete(intent)
    db.session.commit()
    return redirect("/")
""" 
def background_thread():
    
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count}) """


""" @app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
 """
from static.chat3 import getRespuestaIA
def getRespuestaApi(message):
    respuesta='No entiendo la pregunta...'
    respuesta =getRespuestaIA(message)
    return respuesta

@socketio.event
def my_event(message):
    #session['receive_count'] = session.get('receive_count', 0) + 1
    if(str(message['data'])=="I\'m connected!"):
        emit('my_response',
         {'data': 'Estoy conectado!'})
        return
    #usar modelo
    
    emit('my_response',{'data': getRespuestaApi(message['data'])})#RESPUESTA


""" @socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data']},
         broadcast=True) """


""" @socketio.event
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']}) """


""" @socketio.event
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']}) """


""" @socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room']) """


""" @socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data']},
         to=message['room']) """


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!'},
         callback=can_disconnect)


""" @socketio.event
def my_ping():
    emit('my_pong') """


""" @socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0}) """


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


