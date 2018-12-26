from typing import List, Dict
from flask import Flask, render_template, request, session
from flask_pymongo import PyMongo
import json
import sys
import random
import os

# this is the nosql version of the app


app = Flask(__name__, static_url_path='/static')
app.secret_key = '45259547-5106-4f31-84b4-fa33ac37c73e'
app.debug = True

app.config["MONGO_URI"] = "mongodb://mongodb:27017/reach-engine"
mongo = PyMongo(app)

def get_connection():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    return connection, cursor


def kill_connection(connection, cursor):
    cursor.close()
    connection.close()


def get_users_with_username(name):

    con, cur = get_connection()
    sql = "SELECT username FROM user WHERE username = %s"
    user = (name,)
    cur.execute(sql, user)
    results = cur.fetchall()
    kill_connection(con, cur)
    return results

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

            user_found = mongo.db.users.find_one({"name": request.form["new_username"]})

            return "User Already Exists"

            if user_found:
                # user does not exist, so add them
                insrt_sql = "INSERT INTO user (username, wins, losses) VALUES (%s, 0, 0)"
                con, cur = get_connection()
                user = (request.form["new_username"],)
                cur.execute(insrt_sql, user)
                con.commit()  # commit changes to db
                kill_connection(con, cur)
                return "User Created Successfully"
            else:
                # instance of user in database, they already exist
                return "User Already Exists"

        elif 'login_username' in request.form:

            results = get_users_with_username(request.form["login_username"])
            if len(results) == 0:
                return "User Does Not Exist"
            else:
                session['username'] = request.form['login_username']
                return "User Already Exists"

        elif 'player_name' in request.form:

            if check_game_created(request.form["player_name"]) is True:
                return "Found Match"
            status = find_opponent(request.form["player_name"])
            return status
                
    else:
        sys.stdout.flush()
        return app.send_static_file('index.html')


def find_opponent(player_name):
    con, cur = get_connection()
    sql = "SELECT username FROM matchmaking WHERE searching = TRUE AND created > NOW() - INTERVAL 10 SECOND"
    cur.execute(sql)
    results = cur.fetchall()
    print(results)
    all_names = []
    for result in results:
        all_names.append(result[0])
    if len(all_names) == 0 and (player_name not in all_names):
        sql_ins = "INSERT INTO matchmaking (username, searching, created) VALUES (%s, TRUE, NOW())"
        user = (player_name,)
        cur.execute(sql_ins, user)
        con.commit()
        kill_connection(con, cur)
        return "Added to matchmaking table"
    else:
        if player_name in all_names and len(all_names) == 1:
            return "Already in Matchmaking Table Alone"
        else:
            all_names = [x for x in all_names if x != player_name]
            opponent = all_names[0]
            players = (opponent, player_name)
            sql_updt_mat = "UPDATE matchmaking SET searching = FALSE WHERE username = %s OR username = %s"
            cur.execute(sql_updt_mat, players)
            mix_id = random.randint(0,1)
            session['mix_id'] = mix_id
            session['opponent'] = opponent
            session['created'] = True
            players = (opponent, player_name, mix_id)
            sql_game = "INSERT INTO game (score_1,score_2,player_1,player_2,mix_id,active,created) VALUES (0,0,%s,%s,%s,TRUE,NOW())"
            cur.execute(sql_game, players)
            con.commit()
            kill_connection(con, cur)
            return "Found Match"


def check_game_created(player_name):
    con, cur = get_connection()
    sql_chck_game = "SELECT * FROM game WHERE player_1 = %s AND active = TRUE AND created > NOW() - INTERVAL 2 MINUTE"
    player = (player_name,)
    cur.execute(sql_chck_game, player)
    results = cur.fetchall()
    kill_connection(con, cur)
    if len(results) != 0:
        session['created'] = False
        session['opponent'] = results[0][3]
        session['mix_id'] = results[0][4]
        return True
    else:
        return False


@app.route('/game-ai')
def game_ai():
    con, cur = get_connection()
    player = (session['username'],)
    sql_updt_mat = "UPDATE matchmaking SET searching = FALSE WHERE username = %s"
    cur.execute(sql_updt_mat, player)
    con.commit()
    kill_connection(con, cur)
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
