from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound
from werkzeug.security import check_password_hash
from datetime import timedelta
import os

from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity

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

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(users), 200)
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

@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res

    return make_response(jsonify({"error":"User ID not found"}),404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
