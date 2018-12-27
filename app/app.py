from typing import List, Dict
from flask import Flask, render_template, request, session
from flask_pymongo import PyMongo
import json
import sys
import random
import os
import datetime

# this is the nosql version of the app


app = Flask(__name__, static_url_path='/static')
app.secret_key = '45259547-5106-4f31-84b4-fa33ac37c73e'
app.debug = True

app.config["MONGO_URI"] = "mongodb://mongodb:27017/reach-engine"
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
    con, cur = get_connection()
    sql = "SELECT title, content, correct FROM question RIGHT JOIN answer ON question.qid=answer.question_id LIMIT 40"
    cur.execute(sql)
    results = cur.fetchall()  
    d = defaultdict(list)
    for k, *v in results:
        d[k].append(v)
    list(d.items())
    all_results = []
    for key in d:
        d2 = defaultdict(list)
        d2["question"] = key
        all_choices = []
        for x in d[key]:
            all_choices.append(x[0])
            if x[1] == 1:
                d2["correct"] = x[0]
        d2["choices"] = all_choices
        all_results.append(d2)
    if mix_id == 0:
        all_results = all_results[:5]
    else:
        all_results = all_results[5:]
    kill_connection(con, cur)
    return json.dumps(all_results)


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:

            if request.form['new_username'] == "AI":
                return "User Already Exists"

            user_found = users.find_one({"name": request.form["new_username"]})

            print(user_found)
            sys.stdout.flush()

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
    opp = matchmaking.find_one({"username": {"$ne": player_name}, "searching": True, "created": {"$gte": min_time}})
    present = matchmaking.find_one({"username": player_name})

    if opp is None and present is None:  # no opponents and not currently in matchmaking
        matchmaking.insert_one({"username": player_name,
                            "searching": True,
                            "created": datetime.datetime.now()})
        return "Added to matchmaking table"
    
    elif opp is None and present is not None:  # no opponents + in matchmaking already
        return "Already in Matchmaking Table Alone"

    else:
        matchmaking.remove({"$or": [{"username": player_name}, {"username": opp["username"]}]})
        mix_id = random.randint(0,1)
        session['mix_id'] = mix_id
        session['opponent'] = opponent
        session['created'] = True
        games.insert_one({"score_1": 0, "score_2": 0, "player_1": opp["username"], 
                    "player_2": player_name, "mix_id": mix_id, "created": datetime.datetime.now()})

        return "Found Match"


def check_game_created(player_name):

    game = games.find_one({"player_1": player_name})

    if game is not None:
        session['created'] = False
        session['opponent'] = game["player_2"]
        session['mix_id'] = results[0][4]
        return True
    else:
        return False


@app.route('/game-ai')
def game_ai():

    matchmaking.remove({"username": session['username']})
    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent="AI", quiz=quiz)


@app.route('/game', methods = ['GET','POST'])
def game():
    # player 2 created the game
    if request.method == "POST":
        con, cur = get_connection()
        if 'username' in request.form:
            sql_check_scr = "SELECT * from game WHERE player_1 = %s AND player_2 = %s AND active = TRUE AND created > NOW() - INTERVAL 2 MINUTE"
            if session['created'] is False:  # player 1
                players = (request.form['username'], request.form['opponent'])
                cur.execute(sql_check_scr, players)
                results = cur.fetchall()
                opp_score = results[0][1]
                kill_connection(con, cur)
                return str(opp_score)
            else:  # player 2
                players = (request.form['opponent'], request.form['username'])
                cur.execute(sql_check_scr, players)
                results = cur.fetchall()
                opp_score = results[0][0]
                kill_connection(con, cur)
                return str(opp_score)

        if 'username_updt' in request.form:
            score = (request.form["score"], request.form["username_updt"], request.form["opponent_updt"])
            if session['created'] is False:  # player 1
                sql_updt_scr = "UPDATE game SET score_1 = %s WHERE player_1 = %s AND player_2 = %s AND active = TRUE AND created > NOW() - INTERVAL 2 MINUTE"
                cur.execute(sql_updt_scr, score)
                con.commit()
            else:  # player 2
                sql_updt_scr = "UPDATE game SET score_2 = %s WHERE player_2 = %s AND player_1 = %s AND active = TRUE AND created > NOW() - INTERVAL 2 MINUTE"
                cur.execute(sql_updt_scr, score)
                con.commit()
            kill_connection(con, cur)
            return "Score updated"

        if 'username_deact' in request.form:
            update_leaderboard(request.form['username_deact'], request.form['result'])
            players = (request.form['username_deact'], request.form['opponent_deact'])
            sql_deact = "UPDATE game SET active = FALSE WHERE player_1 = %s AND player_2 = %s"
            cur.execute(sql_deact, players)
            con.commit()
            kill_connection(con, cur)
            return "Deactivated Game"

    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent=session['opponent'], quiz=quiz)


def update_leaderboard(username, result):
    con, cur = get_connection()
    sql_lead = ""
    if result == "win":
        sql_lead = "UPDATE user SET wins = wins + 1 WHERE username = %s"
    elif result == "draw":
        sql_lead = "UPDATE user SET draws = draws + 1 WHERE username = %s"
    else:
        sql_lead = "UPDATE user SET losses = losses + 1 WHERE username = %s"
    params = (username,)
    cur.execute(sql_lead, params)
    con.commit()
    kill_connection(con, cur)


@app.route('/leaderboard')
def leaderboard():
    con, cur = get_connection()
    sql_lead = "SELECT * from user"
    cur.execute(sql_lead)
    results = cur.fetchall()
    kill_connection(con, cur)
    return render_template('leaderboard.html', leaderboard=results)
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
