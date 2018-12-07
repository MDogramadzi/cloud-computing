from typing import List, Dict
from flask import Flask, render_template
import mysql.connector
import json

app = Flask(__name__, static_url_path='/static')
app.debug = True

def all_questions() -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'quiz'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM question')
    results = [{"Q": title} for (title) in cursor]
    cursor.close()
    connection.close()

    return results


@app.route('/')
def index() -> str:
    return app.send_static_file('index.html')
    #return json.dumps({'all_questions': all_questions()})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
