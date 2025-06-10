from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import os

# Firebase Realtime Database
import firebase_admin
from firebase_admin import credentials, db

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Conexión a MongoDB Atlas
client = MongoClient(
    "mongodb+srv://al21020011:mrK8BpB3bJwdXXkQ@cluster0.b9qlnhw.mongodb.net/peliculas_db?retryWrites=true&w=majority",
    tls=True,
    tlsCAFile=certifi.where()
)
db_mongo = client["peliculas_db"]
collection = db_mongo["peliculas"]

# Inicializar Firebase Admin con Realtime Database
cred = credentials.Certificate("/etc/secrets/firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://peliculas-app-4530b-default-rtdb.firebaseio.com/'  # <--- CAMBIA si tu URL es distinta
})

# =============================
# PELÍCULAS (MongoDB)
# =============================

@app.route('/movies', methods=['GET'])
def get_movies():
    movies = []
    for movie in collection.find():
        movie["_id"] = str(movie["_id"])
        movies.append(movie)
    return jsonify(movies)

@app.route('/movies', methods=['POST'])
def add_movie():
    data = request.get_json()
    new_movie = {
        "titulo": data.get("titulo"),
        "director": data.get("director"),
        "año": data.get("año"),
        "genero": data.get("genero"),
        "portada": data.get("portada", "https://via.placeholder.com/300x450?text=Sin+Portada"),
        "descripcion": data.get("descripcion", "Sin descripción disponible")
    }
    result = collection.insert_one(new_movie)

    pelicula_id = str(result.inserted_id)
    asientos = {f"{chr(f)}{c}": False for f in range(65, 70) for c in range(1, 6)}  # A1–E5
    db.reference(f"/asientos/{pelicula_id}").set(asientos)

    return jsonify({"mensaje": "Película agregada exitosamente", "id": pelicula_id}), 201

@app.route('/movies/<id>', methods=['PUT'])
def update_movie(id):
    data = request.get_json()
    result = collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "titulo": data.get("titulo"),
            "director": data.get("director"),
            "año": data.get("año"),
            "genero": data.get("genero"),
            "portada": data.get("portada", "https://via.placeholder.com/300x450?text=Sin+Portada"),
            "descripcion": data.get("descripcion", "Sin descripción disponible")
        }}
    )
    if result.matched_count:
        return jsonify({"mensaje": "Película actualizada exitosamente"})
    else:
        return jsonify({"error": "Película no encontrada"}), 404

@app.route('/movies/<id>', methods=['DELETE'])
def delete_movie(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    db.reference(f"/asientos/{id}").delete()
    if result.deleted_count:
        return jsonify({"mensaje": "Película eliminada exitosamente"})
    else:
        return jsonify({"error": "Película no encontrada"}), 404

# =============================
# ASIENTOS (Realtime DB)
# =============================

@app.route('/asientos/<pelicula_id>', methods=['GET'])
def obtener_asientos(pelicula_id):
    ref = db.reference(f"/asientos/{pelicula_id}")
    datos = ref.get()
    return jsonify(datos or {})

@app.route('/asientos/<pelicula_id>', methods=['POST'])
def reservar_asientos(pelicula_id):
    data = request.get_json()
    seleccionados = data.get("asientos", [])

    ref = db.reference(f"/asientos/{pelicula_id}")
    asientos_actuales = ref.get() or {}

    for asiento in seleccionados:
        if asientos_actuales.get(asiento):
            return jsonify({"error": f"Asiento {asiento} ya ocupado"}), 400

    for asiento in seleccionados:
        asientos_actuales[asiento] = True

    ref.set(asientos_actuales)
    return jsonify({"mensaje": "Asientos reservados con éxito", "ocupados": seleccionados})

@app.route('/asientos/<pelicula_id>/init', methods=['POST'])
def inicializar_asientos(pelicula_id):
    asientos = {f"{chr(f)}{c}": False for f in range(65, 70) for c in range(1, 6)}
    db.reference(f"/asientos/{pelicula_id}").set(asientos)
    return jsonify({"mensaje": "Mapa de asientos creado"})

# =============================
# RUN
# =============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
