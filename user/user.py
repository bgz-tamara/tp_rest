from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound
from werkzeug.security import check_password_hash
from datetime import timedelta
import os

from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-secret-change-this"
)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def write(users):
    with open('{}/databases/users.json'.format("."), 'w') as f:
        full = {}
        full['users']=users
        json.dump(full, f)

def check_permission(userid):
    current_user = get_jwt_identity()
    claims = get_jwt()

    return current_user == userid or claims.get("admin", False)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# root message : recup des users en json
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(users), 200) # serialisation en json de objet python "users" pour envoie a l'utilisateur 
    return res

@app.route("/login", methods=['POST'])
def login():
    req = request.get_json()

    if not req:
        return make_response(jsonify({"error":"Missing JSON body"}),400)

    userid = req.get("id")
    password = req.get("password")

    for user in users:
        if str(user["id"]) == str(userid):

            if check_password_hash(user.get("password_hash", ""), password or ""):

                access_token = create_access_token(
                    identity=user["id"],
                    additional_claims={"admin": user["admin"]}
                )

                return make_response(jsonify({
                    "message": "Login successful",
                    "access_token": access_token
                }),200)

            return make_response(jsonify({"error":"Invalid credentials"}),401)

    return make_response(jsonify({"error":"Invalid credentials"}),401)

# root message : recup d'un user en json
@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid): # flask se charge de parser l'url et de recup le parametre du meme nom
    for user in users: # users --> liste des utilisateurs a partir du fichier json
        if str(user["id"]) == str(userid): # verifie correspondance
            res = make_response(jsonify(user),200)
            return res
    return make_response(jsonify({"error":"User ID not found"}),404) # reponse si n'existe pas 

# recup user par nom
@app.route("/usersbyusername", methods=['GET'])
def get_user_byusername(): # pas très Rest rules car parametre caché dans la requête HTTP
    json = ""
    if request.args:
        req = request.args
        for user in users:
            if str(user["name"]) == str(req["name"]):
                json = user

    if not json:
        res = make_response(jsonify({"error":"user name not found"}),500)
    else:
        res = make_response(jsonify(json),200)
    return res

# modif le nom d'un user existant 
@app.route("/users/<userid>/<newusername>", methods=['PUT'])
@jwt_required()
def update_user_username(userid, newusername):
    if not check_permission(userid):
        return make_response(jsonify({
            "error": "Admin permission required"
        }), 403)
        
    for user in users:
        if str(user["id"]) == str(userid):
            user["name"] = newusername
            res = make_response(jsonify(user),200)
            write(users)
            return res

    res = make_response(jsonify({"error":"user ID not found"}),500)
    return res

# delete un film 
@app.route("/users/<userid>", methods=['DELETE'])
@jwt_required()
def del_user(userid):
    if not check_permission(userid):
        return make_response(jsonify({
            "error": "Admin permission required"
        }), 403)

    for user in users:
        if str(user["id"]) == str(userid):
            users.remove(user)
            write(users)
            return make_response(jsonify(user),200)

    res = make_response(jsonify({"error":"user ID not found"}),500)
    return res

# ajout d'un user
@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    req = request.get_json()

    for user in users:
        if str(user["id"]) == str(userid):
            print(user["id"])
            print(userid)
            return make_response(jsonify({"error":"user ID already exists"}),500)

    users.append(req)
    write(users)
    res = make_response(jsonify({"message":"user added"}),200)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
