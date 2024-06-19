import os
from docx import Document
import csv
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def read_document(file_path):
    if file_path is None:
        raise ValueError('file_path cannot be None')

    file_ext = os.path.splitext(file_path)[1]
    if file_ext == '.txt':
        with open(file_path, "r") as file:
            content = file.read()
        return content

    elif file_ext == '.docx':
        doc = Document(file_path)
        content = ""
        for para in doc.paragraphs:
            content += para.text
        return content

    elif file_ext == ".csv":
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            content = ""
            for row in reader:
                content += ','.join(row) + '\n'
        return content

    elif file_ext == ".pdf":
        reader = PdfReader(file_path)
        content = ''
        for page in reader.pages:
            content += page.extract_text()
        return content
    else:
        raise ValueError("File type not supported")


def get_chunks(content: str) -> list:
    if content is None:
        raise ValueError("Content cannot be None")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[" ", ",", "\n", "\n\n"],
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(content)


def get_embeddings(chunks, client, model="text-embedding-3-small"):
    if chunks is None:
        raise ValueError("chunks cannot be None")
    if client is None:
        raise ValueError("client cannot be None")
    embeddings = []
    for chunk in chunks:
        text = chunk.replace("\n", " ")
        embeddings.append(client.embeddings.create(input=[text], model=model).data[0].embedding)
    return embeddings


def save_document(path, client, collection):  # add_document_chunk(embedding, chunk_text, document_id)
    if path is None:
        raise ValueError("path cannot be None")
    if client is None:
        raise ValueError("client cannot be None")
    if collection is None:
        raise ValueError("collection cannot be None")
    document = read_document(path)
    chunks = get_chunks(document)
    embeddings = get_embeddings(chunks, client)
    metadata = [{
        "chunk_id": generate_uuid()
    } for _ in range(len(embeddings))]
    ids = [str(i) for i in range(len(chunks))]
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadata,
        ids=ids
    )


def ask_llm(text, client, collection, model_name="gpt-3.5-turbo"):
    if client is None:
        raise ValueError("client cannot be None")
    if collection is None:
        raise ValueError("collection cannot be None")
    query_chunks = get_chunks(text)
    query_embeddings = get_embeddings(query_chunks, client)
    result = collection.query(
        query_embeddings=query_embeddings,
        n_results=3
    )
    prompt = ""
    for doc in result['documents'][0]:
        prompt += doc
    message = {
        'role': 'user',
        'content': prompt
    }
    response = client.chat.completions.create(
        model=model_name,
        messages=[message]
    )

    chatbot_response = response.choices[0].message.content
    return chatbot_response
