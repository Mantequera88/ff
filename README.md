# CEM El Turo — Chatbot Local

## COM ARRANCAR (VSCode)

### 1. Obre el terminal de VSCode
Terminal → New Terminal  (o Ctrl + ñ)

### 2. Instala les dependències (primer cop)
pip install -r requirements.txt

### 3. Arranca el servidor
python app.py

Hauries de veure:
  Corpus: XXX fragments de 33 pagines HTML
  Servidor CEM El Turo a http://localhost:5000

### 4. Obre el navegador
http://localhost:5000

El chatbot ja funcionara!

---
PROBLEMES HABITUALS
- ModuleNotFoundError: flask  →  pip install -r requirements.txt
- Address already in use      →  Tanca l'altre servidor o canvia el port
- Error de connexio al chat   →  Assegura't que python app.py s'esta executant
- Clau API invalida           →  Canvia DEEPSEEK_API_KEY a app.py

Clau API nova: https://platform.deepseek.com
