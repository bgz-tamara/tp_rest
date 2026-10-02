from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

def write(schedule):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        full = {}
        full['schedule']=schedule               
        json.dump(full, f)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Showtime service!</h1>",200)

# root message : recup des programmes en json
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(schedule), 200) # serialisation en json de objet python "schedules" pour envoie a l'utilisateur 
    return res

# root message : recup d'un booking en json
@app.route("/schedules/<scheduleid>", methods=['GET'])
def get_schedule_byid(scheduleid): # flask se charge de parser l'url et de recup le parametre du meme nom
    for schedule in schedule: # schedule --> liste des horaires a partir du fichier json
        if str(schedule["id"]) == str(scheduleid): # verifie correspondance
            res = make_response(jsonify(schedule),200)
            return res
    return make_response(jsonify({"error":"Schedule ID not found"}),404) # reponse si n'existe pas 

@app.route("/schedules/<date>", methods=['GET'])
def get_schedule_by_date_and_movie(scheduleid): 
    for schedule in schedule: 
        if str(schedule["date"]) == str(date): 
         
            res = make_response(jsonify(schedule),200)
            return res
    return make_response(jsonify({"error":"Schedule ID not found"}),404) # reponse si n'existe pas 


# delete un booking 
@app.route("/schedules/<scheduleid>", methods=['DELETE'])
def del_schedule(scheduleid):
    for schedule in schedule:
        if str(schedule["id"]) == str(scheduleid):
            schedule.remove(schedule)
            write(schedule)
            return make_response(jsonify(schedule),200)

    res = make_response(jsonify({"error":"Schedule ID not found"}),500)
    return res

# ajout d'un booking
@app.route("/schedules/<scheduleid>", methods=['POST'])
def add_schedule(scheduleid):
    req = request.get_json()

    for schedule in schedule:
        if str(schedule["id"]) == str(scheduleid):
            print(schedule["id"])
            print(scheduleid)
            return make_response(jsonify({"error":"Schedule ID already exists"}),500)

    schedule.append(req)
    write(schedule)
    res = make_response(jsonify({"message":"Schedule added"}),200)
    return res


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
