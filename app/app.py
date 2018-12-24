from typing import List, Dict
from flask import Flask, render_template, request, session
import mysql.connector
import json
import sys
import random

app = Flask(__name__, static_url_path='/static')
app.secret_key = '45259547-5106-4f31-84b4-fa33ac37c73e'
app.debug = True

config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'quiz'
        }


def get_connection():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    return connection, cursor


def kill_connection(connection, cursor):
    cursor.close()
    connection.close()


def get_users_with_username(name):

    con, cur = get_connection()
    sql = "SELECT * FROM user WHERE username = %s"
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
                "User Already Exists"

            results = get_users_with_username(request.form["new_username"])

            if len(results) == 0:
                # user does not exist, so add them
                insrt_sql = "INSERT INTO user (username) VALUES (%s)"
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
            print(status)
            return status
                
    else:
        return app.send_static_file('index.html')


def find_opponent(player_name):
    con, cur = get_connection()
    sql = "SELECT username FROM matchmaking WHERE searching = TRUE"
    cur.execute(sql)
    results = cur.fetchall()
    all_names = []
    for result in results:
        all_names.append(result[0])
    if len(all_names) == 0 and (player_name not in all_names):
        sql_ins = "INSERT INTO matchmaking (username, searching) VALUES (%s, TRUE)"
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
            players = (opponent, player_name, mix_id)
            sql_game = "INSERT INTO game (score_1,score_2,player_1,player_2,mix_id) VALUES (0,0,%s,%s,%s)"
            cur.execute(sql_game, players)
            con.commit()
            kill_connection(con, cur)
            return "Found Match"


def check_game_created(player_name):
    print("Check Game Created")
    con, cur = get_connection()
    sql_chck_game = "SELECT * FROM game WHERE player_1 = %s"
    player = (player_name,)
    cur.execute(sql_chck_game, player)
    results = cur.fetchall()
    kill_connection(con, cur)
    if len(results) != 0:
        session['opponent'] = results[0][3]
        return True
    else:
        return False


@app.route('/game-ai')
def game_ai():
    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent="AI", quiz=quiz)


@app.route('/game')
def game():
    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent=session['opponent'], quiz=quiz)


@app.route('/summary')
def summary():
    return render_template('summary.html')
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
