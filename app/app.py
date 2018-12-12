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


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:

            print(request.form["new_username"])

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            sql = "SELECT * FROM user WHERE username = %s"
            user = (request.form["new_username"],)
            cursor.execute(sql, user)
            results = cursor.fetchall()

            print(results)

            sys.stdout.flush()  # forcing prints to console

            if len(results) == 0:
                # user does not exist, so add them
                insrt_sql = "INSERT INTO user (username) VALUES (%s)"
                cursor.execute(insrt_sql, user)
                connection.commit()
                cursor.close()
                connection.close()
                return "User Created Successfully"
            else:
                # instance of user in database, they already exist
                cursor.close()
                connection.close()
                return "User Already Exists"

        else:
            # Start looking for a session for the user
            print("JOINING GAME")
 
    else:
        return app.send_static_file('index.html')
        #return json.dumps({'all_questions': all_questions()})

@app.route('/connect')
def connect() -> str:
    return app.send_static_file('connect.html')
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
