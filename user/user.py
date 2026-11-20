from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

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

@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res

    return make_response(jsonify({"error":"User ID not found"}),404)

@app.route("/users/<userid>/admin", methods=['GET'])
def check_admin(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify({"admin":user["admin"]}),200)
            return res

    return make_response(jsonify({"error":"User ID not found"}),404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
