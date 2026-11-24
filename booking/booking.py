from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
import os

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-secret-change-this"
)

jwt = JWTManager(app)

PORT = 3201
HOST = '0.0.0.0'
MOVIE_URL = 'http://localhost:3200'
SCHEDULE_URL = 'http://localhost:3202'
USER_URL = "http://localhost:3203"

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

def write(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        full = {}
        full['bookings']=bookings
        json.dump(full, f)

def check_permission(userid):
    current_user = get_jwt_identity()
    claims = get_jwt()

    return current_user == userid or claims.get("admin", False)

def movie_is_scheduled(date, movieid) :
   try:
      r = requests.get(f'{SCHEDULE_URL}/schedules/{date}/{movieid}')
   except requests.exceptions.RequestException:
      return None
   return r.status_code == 200

def add_movie_detail_to_tab_movies(movieid, tab_movies_details) :
    try:
        r = requests.get(f"{MOVIE_URL}/movies/{movieid}")
    except requests.exceptions.RequestException:
        return make_response(jsonify({"error": "Movie service is not available"}), 503)
    if r.status_code == 200:
        tab_movies_details.append(r.json())
    else:
        tab_movies_details.append({"id": movieid})
    
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>",200)

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(bookings), 200) # serialisation en json de objet python "bookings" pour envoie a l'utilisateur 
    return res

@app.route("/bookings/<userid>", methods=['GET'])
@jwt_required()
def get_all_booking_of_userid(userid):
    if not check_permission(userid):
        return make_response(jsonify({
            "error": "Missing permission"
        }), 403)
        
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = []                                  
            for dates in booking["dates"]:
                detail_movie = []
                for movieid in dates["movies"]:
                    add_movie_detail_to_tab_movies(movieid, detail_movie)
                res.append({"date": dates["date"], "movies": detail_movie})
            return make_response(jsonify(res), 200)
    return make_response(jsonify({"error": "No bookings for this user founded"}), 404)

@app.route("/bookings/<userid>/<date>/<movie>", methods=['GET'])
@jwt_required()
def get_booking(userid, date, movie): 
    if not check_permission(userid):
        return make_response(jsonify({
            "error": "Missing permission"
        }), 403)

    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            detail_movie = []          
            for dates in booking["dates"]:
                if str(dates["date"]) == str(date):
                    if str(movie) in dates["movies"]:
                        add_movie_detail_to_tab_movies(movie, detail_movie)
                    return make_response(jsonify({"date": dates["date"], "movie": detail_movie}), 200)
        
    return make_response(jsonify({"error":"Booking not found"}),404) 

@app.route("/bookings/<userid>/<date>/<movieid>", methods=['DELETE'])
@jwt_required()
def del_booking(userid,date,movieid):
    if not check_permission(userid):
        return make_response(jsonify({
            "error": "Missing permission"
        }), 403)

    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            for dates in booking["dates"]: 
                if str(dates["date"]) == str(date):
                    if str(movieid) in dates["movies"]:
                        dates["movies"].remove(str(movieid))
                        if len(dates["movies"]) == 0:
                            booking["dates"].remove(dates)
                        if len(booking["dates"]) == 0:
                            bookings.remove(booking)
                        write(bookings)
                        return make_response(jsonify(booking),200)

    res = make_response(jsonify({"error":"booking ID not found"}),500)
    return res

@app.route("/bookings/create", methods=['POST'])
def add_booking():
    req = request.get_json()
    
    scheduled = movie_is_scheduled(req["date"], req["movie"])
    if scheduled is None:
        return make_response(jsonify({"error": "Schedule service is not available"}), 503)
    if not scheduled:
        return make_response(jsonify({"error": "Movie is not scheduled"}), 500)
    
    for booking in bookings:
        if str(booking["userid"]) == str(req["userid"]):
            for dates in booking["dates"]: 
                if str(dates["date"]) == str(req["date"]):
                    if str(req["movie"]) in dates["movies"]:
                        return make_response(jsonify({"error":"Booking already exists"}),500)
                    dates["movies"].append(req["movie"])
                    write(bookings)
                    return make_response(jsonify({"message":"Booking added"}),200)
            booking["dates"].append({"date": req["date"], "movies": [req["movie"]]})
            write(bookings)
            return make_response(jsonify({"message":"Booking added"}),200)
    bookings.append({"userid": req["userid"], "dates": [{"date": req["date"], "movies": [req["movie"]]}]}) 
    write(bookings)
    return make_response(jsonify({"message":"Booking added"}),200)

    
if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
