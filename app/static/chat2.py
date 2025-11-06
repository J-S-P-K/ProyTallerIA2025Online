import random
import json

import torch
import gradio as gr

import logging
import collections
import datetime


from static.model import NeuralNet
from static.nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

import sqlite3
import ast

def chaty():
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
    z= all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]
    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    return z