from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import os

app = Flask(__name__)
CORS(app)

# Conexión segura a MongoDB Atlas usando certificado raíz
client = MongoClient(
    "mongodb+srv://al21020011:mrK8BpB3bJwdXXkQ@cluster0.b9qlnhw.mongodb.net/peliculas_db?retryWrites=true&w=majority",
    tls=True,
    tlsCAFile=certifi.where()
)

# Selección de base de datos y colección
db = client["peliculas_db"]
collection = db["peliculas"]

# Obtener todas las películas
@app.route('/movies', methods=['GET'])
def get_movies():
    movies = []
    for movie in collection.find():
        movie["_id"] = str(movie["_id"])  # Convertir ObjectId a string
        movies.append(movie)
    return jsonify(movies)

# Añadir una película
@app.route('/movies', methods=['POST'])
def add_movie():
    data = request.get_json()
    new_movie = {
        "titulo": data.get("titulo"),
        "director": data.get("director"),
        "año": data.get("año"),
        "genero": data.get("genero"),
        "portada": data.get("portada")
    }
    result = collection.insert_one(new_movie)
    return jsonify({"mensaje": "Película agregada exitosamente", "id": str(result.inserted_id)}), 201

# Actualizar una película
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
            "portada": data.get("portada")
        }}
    )
    if result.matched_count:
        return jsonify({"mensaje": "Película actualizada exitosamente"})
    else:
        return jsonify({"error": "Película no encontrada"}), 404

# Eliminar una película
@app.route('/movies/<id>', methods=['DELETE'])
def delete_movie(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"mensaje": "Película eliminada exitosamente"})
    else:
        return jsonify({"error": "Película no encontrada"}), 404

# Configuración para producción (Render)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
