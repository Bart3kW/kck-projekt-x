from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
USERS_FILE = 'users.json'

def load_users():
    """Ładuje dane użytkowników z pliku JSON."""
    if not os.path.exists(USERS_FILE):
        # Tworzy pusty plik, jeśli nie istnieje
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Zapisuje dane użytkowników do pliku JSON."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4) # 'indent=4' dla ładniejszego formatowania

@app.route('/register', methods=['POST'])
def register():
    """Endpoint do rejestracji nowego użytkownika."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    users = load_users()
    if username in users:
        return jsonify({"message": "Username already exists"}), 409 # Conflict (użytkownik już istnieje)

    # W prawdziwej aplikacji hasłowałbyś hasła!
    users[username] = {"password": password}
    save_users(users)
    return jsonify({"message": "Registration successful"}), 201 # Created

@app.route('/login', methods=['POST'])
def login():
    """Endpoint do logowania użytkownika."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    users = load_users()
    if username in users and users[username]["password"] == password:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401 # Unauthorized (nieprawidłowe dane)

if __name__ == '__main__':
    # Uruchamia serwer na adresie http://127.0.0.1:5000/
    # debug=True automatycznie odświeża serwer po zmianach kodu i pokazuje błędy
    app.run(debug=True, port=5000)
