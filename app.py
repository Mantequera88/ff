import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ── Configuración DeepSeek ────────────────────────────────────────────────────
DEEPSEEK_API_KEY = "sk-9946d7c4b397427681466a5c9a98934b"   # <-- REEMPLAZA si caduca

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ── Cargar HTMLs en memoria al arrancar ───────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS = []   # lista de (filename, text_chunk)

def _html_to_text(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text

def _build_corpus():
    html_files = [f for f in os.listdir(BASE_DIR) if f.endswith('.html')]
    for fname in html_files:
        path = os.path.join(BASE_DIR, fname)
        text = _html_to_text(path)
        words = text.split()
        for i in range(0, len(words), 550):
            chunk = ' '.join(words[max(0, i-50):i+600])
            if chunk.strip():
                CORPUS.append((fname, chunk))
    print(f"✅ Corpus: {len(CORPUS)} fragments de {len(html_files)} pagines HTML")

_build_corpus()

def buscar_contexto(pregunta, top_k=5):
    stops = {
        'el','la','los','las','de','del','en','y','a','que','es','se','un','una',
        'para','con','por','como','mas','este','esta','no','al','le',
        'els','les','per','com','mes','aquest','aquesta','o','pero','i'
    }
    words = [w.lower() for w in re.findall(r'\w+', pregunta) if w.lower() not in stops and len(w) > 2]
    scored = []
    for fname, chunk in CORPUS:
        chunk_lower = chunk.lower()
        score = sum(chunk_lower.count(w) for w in words)
        if score > 0:
            scored.append((score, fname, chunk))
    scored.sort(reverse=True)
    return [chunk for _, _, chunk in scored[:top_k]]

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(BASE_DIR, path)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json(force=True)
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"error": "Missatge buit"}), 400

        fragmentos = buscar_contexto(user_message, top_k=5)
        contexto = "\n\n---\n\n".join(fragmentos) if fragmentos else "No s'ha trobat informacio especifica."

        system_prompt = f"""Eres un asistente virtual del CEM El Turo, un complejo deportivo municipal de La Llagosta (Barcelona).
Responde en el mismo idioma que el usuario (catalan o castellano).
Usa la informacion del contexto web para responder con precision.
Si no esta en el contexto, sugiere llamar al 93 545 15 50 o visitar www.cemelturo.cat.

CONTEXTO:
{contexto}

Normas: se breve, amable, no inventes datos."""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.3
        )

        bot_response = response.choices[0].message.content
        return jsonify({"response": bot_response})

    except Exception as e:
        print(f"[ERROR /chat] {e}")
        return jsonify({"error": f"Error intern: {str(e)}"}), 500

if __name__ == '__main__':
    print("Servidor CEM El Turo a http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
