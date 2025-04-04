from flask import Flask, jsonify, request
import firebase_admin
import random
from firebase_admin import credentials, firestore
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)

load_dotenv()

cred = credentials.Certificate("api.json")
firebase_admin.initialize_app(cred)

# PEGA A VARIAVEL DE AMBIENTE DO FIREBASE E CONVERTE PARA JSON
FBKEY = json.loads(os.getenv('CONFIG_FIREBASE'))

db = firestore.client()


# ROTA PRINCIPAL DE TESTE
@app.route('/')
def index():
    return 'API TÁ ON'

#METODO GET CHARADA ALEATÓRIA
@app.route('/charadas', methods=['GET'])
def charada_aleatoria():
    charadas = []
    lista = db.collection('charadas').stream()
    for item in lista:
        charadas.append(item.to_dict())

    if charadas:
        return jsonify(random.choice(charadas)), 200

    else:
        return jsonify({'erro': 'não há charadas cadastradas'}), 404


@app.route('/charadas/<id>', methods=['GET'])
def busca(id):
    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get().to_dict()

    if doc:
        return jsonify(doc), 200
    else:
        return jsonify({'erro': 'charada não encontrada'}), 404

@app.route('/charadas', methods=['POST'])
def adicionar_charada():
    dados = request.json

    if "pergunta" not in dados or "resposta" not in dados:
        return jsonify({'erro': 'dados inválidos'}), 400
    
    #Contador
    contador_ref = db.collection('controle_id').document('contador')
    contador_doc = contador_ref.get().to_dict()
    ultimo_id = contador_doc.get('id')
    novo_id = int(ultimo_id) + 1
    contador_ref.update({'id': novo_id})

    db.collection('charadas').document(str(novo_id)).set({
        "id": novo_id,
        "pergunta": dados["pergunta"],
        "resposta": dados["resposta"]
    })
    return jsonify({'mensagem': 'Charada cadastrada'}), 201

@app.route('/charadas', methods=['PUT'])
def alterar_charada(id):
    dados = request.json

    if "pergunta" not in dados or "resposta" not in dados:
        return jsonify({'erro': 'dados inválidos'}), 400

    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({'erro': 'charada não encontrada'}), 404
    
    doc_ref.delete()
    return jsonify({'mensagem': 'Charada deletada'}), 200

if __name__ == '__main__':
    app.run(debug=True)