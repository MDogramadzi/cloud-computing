from typing import List, Dict
from flask import Flask, render_template, request, session
from flask_pymongo import PyMongo
import json
import sys
import random
import os
import datetime
from bson import ObjectId

# this is the nosql version of the app


app = Flask(__name__, static_url_path='/static')
app.secret_key = '45259547-5106-4f31-84b4-fa33ac37c73e'

app.config["MONGO_URI"] = "mongodb://mongo:27017/reach-engine"
mongo = PyMongo(app)


# define the collections (tables), fine to do it here as they are only created
# if they do not exist already

users = mongo.db["users"]
matchmaking = mongo.db["matchmaking"]
games = mongo.db["games"]
questions = mongo.db["questions"]  # should be the only table that needs seeding (init.json)



from collections import defaultdict
def get_questions_for_quiz():

    mix_id = 0
    try:
        mix_id = session['mix_id']
    except KeyError:
        mix_id = random.randint(0,1)

    question_list = questions.find().limit(10)

    all_questions = []
    for question in question_list:
        d = defaultdict(list)
        d["question"] = question["title"]
        d["choices"] = question["choices"]
        d["correct"] = question["choices"][0]
        all_questions.append(d)

    if mix_id == 0:
        all_questions = all_questions[:5]
    else:
        all_questions = all_questions[5:]

    return json.dumps(all_questions)


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:

            if request.form['new_username'] == "AI":
                return "User Already Exists"

            if not request.form['new_username'].isalnum() or request.form['new_username'] == "":
                return "Invalid Input Format"

            user_found = users.find_one({"name": request.form["new_username"]})

            if user_found is None: 
                # user does not exist, so add them
                users.insert_one({"name": request.form["new_username"],
                                        "wins": 0,
                                        "losses": 0,
                                        "draws": 0})
                return "User Created Successfully"
            else:
                # instance of user in database, they already exist
                return "User Already Exists"

        elif 'login_username' in request.form:

            user_found = users.find_one({"name": request.form["login_username"]})
            if user_found is not None:
                session['username'] = request.form['login_username']
                return "User Already Exists"
            else:
                return "User Does Not Exist"

        elif 'player_name' in request.form:

            if check_game_created(request.form["player_name"]) is True:
                return "Found Match"
            status = find_opponent(request.form["player_name"])
            return status
                
    else:

        return app.send_static_file('index.html')


def find_opponent(player_name):
    
    # check matchmaking table and find if anyone is searching, within reasonable time
    min_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
    opp = matchmaking.find_one_and_delete({"username": {"$ne": player_name}, "created": {"$gte": min_time}})
    present = matchmaking.find_one({"username": player_name})

    if opp is None and present is None:  # no opponents and not currently in matchmaking
        matchmaking.insert_one({"username": player_name,
                                "created": datetime.datetime.now()})
        return "Added to matchmaking table"
    
    elif opp is None and present is not None:  # no opponents + in matchmaking already
        return "Already in Matchmaking Table Alone"

    else:
        mix_id = random.randint(0,1)
        session['mix_id'] = mix_id
        session['opponent'] = opp["username"]
        session['created'] = True
        games.insert_one({"score_1": 0, "score_2": 0, "player_1": opp["username"], 
                    "player_2": player_name, "mix_id": mix_id, "created": datetime.datetime.now()})

        return "Found Match"


def check_game_created(player_name):
    min_time = datetime.datetime.now() - datetime.timedelta(seconds=80)
    game = games.find_one({"player_1": player_name, "created": {"$gte": min_time}})

    if game is not None:
        session['created'] = False
        session['opponent'] = game["player_2"]
        session['mix_id'] = game["mix_id"]
        return True
    else:
        return False


# load-testing
@app.route('/metrics', methods = ['POST'])
def metrics():

    quiz = get_questions_for_quiz()
    return render_template('game.html', username="Guest", opponent="AI", quiz=quiz)


@app.route('/game-ai')
def game_ai():

    matchmaking.remove({"username": session['username']})
    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent="AI", quiz=quiz)


@app.route('/game', methods = ['GET','POST'])
def game():
    # player 2 created the game
    if request.method == "POST":
        min_time = datetime.datetime.now() - datetime.timedelta(seconds=80)
        if 'username' in request.form:
            if session['created'] is False:  # player 1

                game = games.find_one({"player_1": request.form['username'], "player_2": request.form['opponent'], "created": {"$gte": min_time}})
                opp_score = game["score_2"]
                return str(opp_score)

            else:  # player 2

                game = games.find_one({"player_1": request.form['opponent'], "player_2": request.form['username'], "created": {"$gte": min_time}})
                opp_score = game["score_1"]
                return str(opp_score)

        if 'username_updt' in request.form:

            if session['created'] is False:  # player 1

                query = { "player_1": request.form["username_updt"], "player_2": request.form["opponent_updt"], "created": {"$gte": min_time} }
                newvalues = { "$set": { "score_1": request.form["score"] } }
                games.update_one(query, newvalues)

            else:  # player 2

                query = { "player_1": request.form["opponent_updt"], "player_2": request.form["username_updt"], "created": {"$gte": min_time} }
                newvalues = { "$set": { "score_2": request.form["score"] } }
                games.update_one(query, newvalues)

            return "Score updated"

        if 'username_deact' in request.form:

            games.remove({"player_1": request.form['username_deact']}, 
                        {"player_2": request.form['opponent_deact']})

            update_leaderboard(request.form['username_deact'], request.form['result'])

            return "Deactivated Game"

    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent=session['opponent'], quiz=quiz)


def update_leaderboard(username, result):

    query = { "name": username }
    if result == "win":
        newvalues = { "$inc": { "wins": 1 } }
        users.update_one(query, newvalues)
    elif result == "draw":
        newvalues = { "$inc": { "draws": 1 } }
        users.update_one(query, newvalues)
    else:
        newvalues = { "$inc": { "losses": 1 } }
        users.update_one(query, newvalues)


@app.route('/leaderboard')
def leaderboard():
    results = users.find()
    results_arr = []
    for result in results:
        results_arr.append(result)
    return render_template('leaderboard.html', leaderboard=results_arr)
	

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0') 
