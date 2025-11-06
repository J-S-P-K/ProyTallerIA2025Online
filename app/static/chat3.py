import random
import json
import sqlite3
import ast
import torch

from static.model import NeuralNet
from static.nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def getRespuestaIA(texto):
    conn = None
    def product_row_to_dict(i):
        return {"tag": i[1], "patterns": [str(i[2])], "responses":[str(i[3])]}
    try:
        conn=sqlite3.connect('static/intents.db')
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

    FILE = "static/data.pth"
    
    data = torch.load(FILE)
    #print("data" ,data)
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    bot_name = "Chatbot"
    #print("Let's chat! (type 'quit' to exit)")
    #while True:
        # sentence = "do you use credit cards?"
    #sentence = input("You: ")
    #if sentence == "quit":
    #   break

    texto = tokenize(str(texto))
    #print("Tokenizado", texto)
    X = bag_of_words(texto, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]
    #print("tag ",tag)

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    #print("Probabilidad: ",prob.item())
    if prob.item() > 0.75:
        for intent in intents['intents']:
            #print(intent["tag"]," == ",tag)

            if tag == intent["tag"]:
                return(f"{bot_name}: {random.choice(intent['responses'])}")
            else:
                pass
    if prob.item() > 0.25:
        for intent in intents['intents']:
            #print(intent["tag"]," == ",tag)

            if tag == intent["tag"]:
                return(f"{bot_name}: {random.choice(intent['responses'])}")
            else:
                pass
    return(f"{bot_name}: No entiendo la pregunta...")
    