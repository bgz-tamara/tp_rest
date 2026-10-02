from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

def write(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        full = {}
        full['bookings']=bookings
        json.dump(full, f)

def movie_is_scheduled(date, movieId) :
   try:
      r = request.get('https://localhost:3201/schedule/{date}');
   except request.exceptions.RequestException:
      return None
   if r.status_code !== 200
      return false;
   else 
      for entry in r.json()["schedule"]:
         if entry["date"] == date:
            return movie_id in entry["movies"]
         return False

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>",200)

# root message : recup des bookings en json
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(bookings), 200) # serialisation en json de objet python "bookings" pour envoie a l'utilisateur 
    return res

# root message : recup d'un booking en json
@app.route("/bookings/<bookingid>", methods=['GET'])
def get_booking_byid(bookingid): # flask se charge de parser l'url et de recup le parametre du meme nom
    for booking in bookings: # bookings --> liste des reservations a partir du fichier json
        if str(booking["id"]) == str(bookingid): # verifie correspondance
            res = make_response(jsonify(booking),200)
            return res
    return make_response(jsonify({"error":"Booking ID not found"}),404) # reponse si n'existe pas 

# delete un booking 
@app.route("/bookings/<bookingid>", methods=['DELETE'])
def del_booking(bookingid):
    for booking in bookings:
        if str(booking["id"]) == str(bookingid):
            bookings.remove(booking)
            write(bookings)
            return make_response(jsonify(booking),200)

    res = make_response(jsonify({"error":"booking ID not found"}),500)
    return res

# ajout d'un booking
@app.route("/bookings/<bookingid>", methods=['POST'])
def add_booking(bookingid):
    req = request.get_json()

    for booking in bookings:
        if str(booking["id"]) == str(bookingid):
            print(booking["id"])
            print(bookingid)
            return make_response(jsonify({"error":"booking ID already exists"}),500)

    bookings.append(req)
    write(bookings)
    res = make_response(jsonify({"message":"booking added"}),200)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
