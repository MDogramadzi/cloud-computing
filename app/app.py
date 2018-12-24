from typing import List, Dict
from flask import Flask, render_template, request, session
import mysql.connector
import json
import sys

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
    con, cur = get_connection()
    sql = "SELECT title, content, correct FROM question RIGHT JOIN answer ON question.qid=answer.question_id ORDER BY RAND() LIMIT 40"
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
    kill_connection(con, cur)
    return json.dumps(all_results)


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:

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
        all_names.remove(player_name)
        opponent = all_names[0]
        sql_game = "INSERT INTO game (score_1, score_2, player_1, player_2 VALUES (0,0,%s,%s)"
        players = (opponent, player_name)
        cur.execute(sql_game, players)
        con.commit()
        kill_connection(con, cur)
        return "Match with the first entry in results"



@app.route('/game-ai')
def game_ai():
    quiz = get_questions_for_quiz()
    return render_template('game.html', username=session["username"], opponent="AI", quiz=quiz)


@app.route('/summary')
def summary():
    return render_template('summary.html')
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
