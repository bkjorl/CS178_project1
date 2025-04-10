from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from Flask!</h1>'

import pymysql
import creds 

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.db,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


#display the sqlite query in a html table
def display_html(rows):
    html = ""
    html += """<table><tr><th>title</th><th>release_date</th><th>runtime</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td></tr>"
    html += "</table></body>"
    return html


@app.route("/viewmovie")
def viewdb():
    rows = execute_query("""SELECT title, release_date, runtime
                FROM movie
                ORDER BY release_date
                Limit 50""")
    return display_html(rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
