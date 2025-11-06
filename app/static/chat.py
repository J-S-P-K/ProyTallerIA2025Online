import random
import json
import torch
import gradio as gr
import logging
import collections
import datetime
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import sqlite3
import ast
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

conn = None
def product_row_to_dict(i):
    return {"tag": i[1], "patterns": [str(i[2])], "responses":[str(i[3])]}
try:
    conn=sqlite3.connect('intents.db')
    c = conn.cursor()
    c.execute('''SELECT *
               FROM intents'''
              )
    conn.commit() 
    p = []
    for p2 in c.fetchall():
        p.append(product_row_to_dict(p2)) 
    rowsdb ='''{"intents": ''',p,'''} '''
    rowsdb=dict()
    rowsdb["intents"] =p
    """ intents = json.load(rowsdb)
    print(intents) """
    ini_string = json.dumps(rowsdb)
    intents =ini_string
    intents = ast.literal_eval(intents)
    #print(intents)
except Exception as e:
    print(e)
finally:
    if conn:
        conn.close() 
""" with open('intents.json', 'r',encoding='utf-8') as json_data:
    intents = json.load(json_data) """
FILE = "data.pth"
data = torch.load(FILE)
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

#css=".gradio-container {background-color: red;width: 400px!important;height: 300px!important;}"
with gr.Blocks(theme=gr.themes.Default(spacing_size=gr.themes.sizes.spacing_sm, radius_size=gr.themes.sizes.radius_none)) as demo:
        with gr.Column(scale=0.08):
                chatbot = gr.Chatbot(label="Chat")
                #atbot.scale(0.2)
                msg = gr.Textbox(label="Ingrese su consulta: ")
                clear = gr.ClearButton([msg, chatbot])
                #loggggg
                def write_to_log(value):
                    """Write message to a log file"""
                    file_object= open("log.txt", "a", encoding='utf-8')
                    event_time = str(datetime.datetime.now())
                    data = collections.OrderedDict()
                    data['time'] = event_time
                    data['event'] = "error"
                    data['details'] = "No se entiende la pregunta"
                    data['value'] = value
                    json.dump(data, file_object, separators=(', ', ':'))
                    file_object.write('\n')
                #respuesta
                def respond(message, chat_history):
                    message2 = tokenize(message)
                    X = bag_of_words(message2, all_words) 
                    X = X.reshape(1, X.shape[0])
                    X = torch.from_numpy(X).to(device)

                    output = model(X)
                    _, predicted = torch.max(output, dim=1)

                    tag = tags[predicted.item()]
                    probs = torch.softmax(output, dim=1)
                    prob = probs[0][predicted.item()]
                    if prob.item() > 0.75:
                        for intent in intents['intents']:
                            if tag == intent["tag"]:
                                bot_message = random.choice(intent['responses'])
                    else:
                        bot_message = "No entiendo la pregunta..."
                        write_to_log(message)
                    chat_history.append((message, bot_message))
                    return "", chat_history

                msg.submit(respond, [msg, chatbot], [msg, chatbot])
demo.launch()