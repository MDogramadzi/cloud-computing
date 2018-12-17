from typing import List, Dict
from flask import Flask, render_template, request
import mysql.connector
import json
import sys

app = Flask(__name__, static_url_path='/static')
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
                return "User Already Exists"
 
    else:
        return app.send_static_file('index.html')
        

@app.route('/connect')
def connect() -> str:
    return app.send_static_file('connect.html')
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
