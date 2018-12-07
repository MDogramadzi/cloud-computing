from typing import List, Dict
from flask import Flask, render_template, request
from flask.ext.mysql import MySQL 
import json

app = Flask(__name__, static_url_path='/static')
app.debug = True

    # config = {
    #     'user': 'root',
    #     'password': 'root',
    #     'host': 'db',
    #     'port': '3306',
    #     'database': 'quiz'
    # }

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'quiz'
app.config['MYSQL_DATABASE_HOST'] = 'db'
mysql.init_app(app)

conn = mysql.connect()

cursor = conn.cursor()


@app.route('/' , methods = ['GET','POST'])
def index() -> str:
    if request.method == "POST":
        if 'new_username' in request.form:
            # Check if user exists in database
            # If yes, then return "User already exists"
            # If no, then add user into database and return "User added successfully"
            
            check_user = (
                "SELECT user, COUNT(*) FROM user WHERE username = %s",
        (request.form['new_username'])
            )
            cursor.execute(check_user)
            row_count = result.rowcount
            if row_count == 0:
            insert_user = (
                "INSERT INTO user (new_username) " "VALUES (%s)"
            )
            user_name = request.form['new_username']
            cursor.execute(insert_user, user_name)
            conn.commit()
        else:
            console.log("USER NOT FOUND")
            # Start looking for a session for the user, username
 
    else:
        return app.send_static_file('index.html')
        #return json.dumps({'all_questions': all_questions()})

@app.route('/connect')
def connect() -> str:
    return app.send_static_file('connect.html')
	

if __name__ == '__main__':
    app.run(host='0.0.0.0')
