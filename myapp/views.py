import chromadb
from openai import OpenAI
from app import app
from flask import jsonify, request
from .utils import save_document, ask_llm
import os
from dotenv import load_dotenv

env_file_path = os.path.join(os.getcwd(), '.envs', '.python')
load_dotenv(env_file_path)
api_key = os.getenv('OPENAI_API_KEY')

client = None
client_db = None
collection = None


@app.route('/load_app', methods=['POST'])
def load_app():
    global client
    global client_db
    if api_key is None:
        return jsonify({'error': 'No OpenAI API key provided!',
                        "status_code": 400}), 400
    client = OpenAI(api_key=api_key)
    client_db = chromadb.Client()

    return jsonify({"message": "OK",
                    "status_code": 200}), 200


@app.route('/add_document', methods=['POST'])
def add_document():
    global collection
    if client_db is None or client is None:
        return jsonify({'error': 'Chroma DB or OpenAI model not initialized. Please load the app first.',
                        "status_code": 400}), 400
    collection = client_db.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )
    data = request.json
    path = data['path']
    if path is None:
        return jsonify({'error': 'No document path provided!',
                        "status_code": 400}), 400
    save_document(path, client, collection)

    return jsonify({"message": "OK",
                    "status_code": 200}), 200


@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    text = data['text']
    if text is None:
        return jsonify({'error': 'No text provided!',
                        "status_code": 400}), 400
    response = ask_llm(text, client, collection)

    return jsonify({"message": "OK",
                    "status_code": 200,
                    "response": response}), 200

