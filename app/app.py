from typing import List, Dict
from flask import Flask, render_template, request
import mysql.connector
import json
import sys

app = Flask(__name__, static_url_path='/static')
app.debug = True


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:

            print("Checking User")

            config = {
                'user': 'root',
                'password': 'root',
                'host': 'db',
                'port': '3306',
                'database': 'quiz'
            }

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            print("###")
            cursor.execute("SELECT * FROM user")
            print(cursor.fetchall())
            cursor.close()
            connection.close()
            print("###")
            sys.stdout.flush()

            return "User Created Successfully"
        else:
            # Start looking for a session for the user, username
            print("JOINING GAME")
 
    else:
        return app.send_static_file('index.html')
        #return json.dumps({'all_questions': all_questions()})

@app.route('/connect')
def connect() -> str:
    return app.send_static_file('connect.html')
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
