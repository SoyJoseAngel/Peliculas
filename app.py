from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Base de datos simulada (en memoria)
movies = []
next_id = 1

# Obtener todas las películas
@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies)

# Añadir una película
@app.route('/movies', methods=['POST'])
def add_movie():
    global next_id
    data = request.get_json()
    new_movie = {
        "id": next_id,
        "titulo": data.get("titulo"),
        "director": data.get("director"),
        "año": data.get("año"),
        "genero": data.get("genero")
    }
    movies.append(new_movie)
    next_id += 1
    return jsonify({"mensaje": "Película agregada exitosamente", "id": new_movie["id"]}), 201

# Actualizar una película
@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.get_json()
    for movie in movies:
        if movie["id"] == movie_id:
            movie["titulo"] = data.get("titulo", movie["titulo"])
            movie["director"] = data.get("director", movie["director"])
            movie["año"] = data.get("año", movie["año"])
            movie["genero"] = data.get("genero", movie["genero"])
            return jsonify({"mensaje": "Película actualizada exitosamente"})
    return jsonify({"error": "Película no encontrada"}), 404

# Eliminar una película
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    global movies
    movies = [movie for movie in movies if movie["id"] != movie_id]
    return jsonify({"mensaje": "Película eliminada exitosamente"})

if __name__ == '__main__':
    app.run(debug=True)
