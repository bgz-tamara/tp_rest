from flask import Flask, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__) # "app .run" app = serveur flask => serveur web (capable de recevoir des requetes et d'envoyerdes rep http)

PORT = 3200 #choisi comme ca
HOST = '0.0.0.0' 

with open('{}/databases/movies.json'.format("."), 'r') as jsf:
    movies = json.load(jsf)["movies"] #extrait movies de la structure json (tableau de films)
    print(movies)

def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        full = {}
        full['movies']=movies
        json.dump(full, f)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# root message : recup des movies en json
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200) # serialisation en json de objet python "movies" pour envoie a l'utilisateur 
    return res

# root message : recup d'un movie en json
@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid): # flask se charge de parser l'url et de recup le parametre du meme nom
    for movie in movies: # movies --> liste des films a partir du fichier json
        if str(movie["id"]) == str(movieid): # verifie correspondance
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error":"Movie ID not found"}),404) # reponse si n'existe pas 

# recup film par titre 
@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle(): # pas très Rest rules car parametre caché dans la requête HTTP
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json = movie

    if not json:
        res = make_response(jsonify({"error":"movie title not found"}),500)
    else:
        res = make_response(jsonify(json),200)
    return res

# modif de la note d'un film existant 
@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = rate
            res = make_response(jsonify(movie),200)
            write(movies)
            return res

    res = make_response(jsonify({"error":"movie ID not found"}),500)
    return res

# delete un film 
@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie),200)

    res = make_response(jsonify({"error":"movie ID not found"}),500)
    return res

# ajout d'un film
@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid):
    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            print(movie["id"])
            print(movieid)
            return make_response(jsonify({"error":"movie ID already exists"}),500)

    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res


if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
