from flask import Flask, render_template, request, jsonify, make_response
import json
import requests
from werkzeug.exceptions import NotFound
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
import os

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'
MOVIE_URL = "http://localhost:3200"

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedules = json.load(jsf)["schedule"]

def write(schedule):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        full = {}
        full['schedule']=schedules               
        json.dump(full, f)

def check_admin():
    claims = get_jwt()
    return claims.get("admin", False)

def add_movie_detail_to_tab_movies(movieid, tab_movies_details) :
    try:
        r = requests.get(f"{MOVIE_URL}/movies/{movieid}")
    except requests.exceptions.RequestException:
        return make_response(jsonify({"error": "Movie service is not available"}), 503)
    if r.status_code == 200:
        tab_movies_details.append(r.json())
    else:
        tab_movies_details.append({"id": movieid})
    
def movie_is_existing(movieid):
    try:
        r = requests.get(f'{MOVIE_URL}/movies/{movieid}')
    except requests.exceptions.ConnectionError:
        return None
    return r.status_code == 200
        
# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Showtime service!</h1>",200)

# root message : recup des programmes en json
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(schedules), 200) # serialisation en json de objet python "schedules" pour envoie a l'utilisateur 
    return res

@app.route("/schedules/<date>/<movieid>", methods=['GET'])
def get_schedule_by_date_and_movie(date, movieid): 
    detail_movie = []
    for schedule in schedules:       
        if str(schedule["date"]) == str(date):
            if str(movieid) in schedule["movies"]:
                add_movie_detail_to_tab_movies(movieid, detail_movie)
                return make_response(jsonify({"date": schedule["date"], "movie": detail_movie}), 200)
            return make_response(jsonify({"error": "Movie is not scheduled at this date"}), 404)
    return make_response(jsonify({"error":"Schedule not found"}),404) 

@app.route("/schedules/<movieid>", methods=['GET'])
def get_schedules_by_movie(movieid): 
    date_tab = []
    for schedule in schedules:     
        if str(movieid) in schedule["movies"]:  
            date_tab.append(schedule["date"])
    
    if len(date_tab)==0:
        return make_response(jsonify({"error":"No schedule found for this movie"}),404) 
    return make_response(jsonify({"movie": movieid, "dates": date_tab}), 200)
    
# delete un booking 
@app.route("/schedules/<date>/<movieid>", methods=['DELETE'])
@jwt_required()
def del_schedule(date,movieid):
    if not check_admin():
        return make_response(jsonify({
            "error": "Admin permission required"
        }), 403)

    for schedule in schedules:
        if str(schedule["date"]) == str(date):
            if str(movieid) in schedule["movies"]:
                schedule["movies"].remove(str(movieid))
                if len(schedule["movies"]) == 0 :
                    schedules.remove(schedule)
                write(schedules)
                return make_response(jsonify(schedule),200)

    res = make_response(jsonify({"error":"Schedule ID not found"}),500)
    return res

# ajout d'un booking
@app.route("/schedules/create", methods=['POST'])
@jwt_required()
def add_schedule():
    if not check_admin():
        return make_response(jsonify({
            "error": "Admin permission required"
        }), 403)
        
    req = request.get_json()
    
    movie_exists = movie_is_existing(req["movie"])
    if movie_exists == None:
        return make_response(jsonify({"error": "Service de film ne tourne pas"}), 503)
    if not movie_exists :
        return make_response(jsonify({"error": "Movie avec l'id : {} n'a pas été trouvé".format(req["movie"])}), 404)
    
    for schedule in schedules:
        if str(schedule["date"]) == str(req["date"]):
            if str(req["movie"]) in schedule["movies"]:
                return make_response(jsonify({"error":"Schedule already exists"}),500)
            schedule["movies"].append(req["movie"])
            write(schedules)
            return make_response(jsonify({"message":"Schedule added"}),200)
    schedules.append({"date": req["date"], "movies": [req["movie"]]})
    write(schedules)
    return make_response(jsonify({"message":"Schedule added"}),200)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT, debug=True)
