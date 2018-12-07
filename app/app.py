from typing import List, Dict
from flask import Flask, render_template, request
import pymysql
import json


app = Flask(__name__, static_url_path='/static')
app.debug = True

db = pymysql.connect("db", "root", "root", "quiz")
cursor = db.cursor()


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:
            print("###")
            cursor.execute("SELECT * FROM user")
            print(cursor.fetchall())
            print("###")
            #cursor.execute("SELECT * from user")
            #data = cursor.fetchone()
            #print(data)
            return "HELLO"
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
