from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash, session #session was added with the help of ChatGPT
import pymysql
import creds 
import boto3


app = Flask(__name__)
app.secret_key = 'your_secret_key' 

#connecting to dynamodb database
TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

#app routes
#home page - sign in 
@app.route('/')
def home():
    return render_template('home.html')
    #options are sign into account with will rediect to user home page or too create an account

@app.route('/login', methods=['POST'])
def login():
    email = request.form['Email']
    password = request.form['Password']

    try:
        response = table.get_item(Key={'email': email})
        user = response.get('Item')

        if user and user['password'] == password:  # In real apps, use hashed passwords
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('user_home'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('home'))

    except Exception as e:
        print("DynamoDB error:", e)
        flash('An error occurred during login.', 'danger')
        return redirect(url_for('home'))

@app.route('/user_home')
def dashboard():
    user_email = session.get('user')  # assuming you saved the email during login
    if not user_email:
        flash('Please log in first.', 'warning')
        return redirect(url_for('home'))
    return render_template('user_home.html', user_email=user_email)


#add user page
    #add user function and then redirect to home page
@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        table.put_item (
            Item={
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Password": password,
            }
        )
        
        flash('User added successfully!', 'success')
        return redirect(url_for('home'))
    else:
        return render_template('add_user.html')
    
#user homepage

    #list favorite genre 
    #lsit movies that are also in that genre and came out within a similar timeframe
        #RDS and joins

    #option to update user
    #option to delete user

#delete user
@app.route('/delete-user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        email = request.form['email']

        table.delete_item(
            Key={
            "Email": email,
            }
        )
        flash('User deleted successfully!', 'warning')
        return redirect(url_for('home'))
    else:
        return render_template('delete_user.html')



























    


@app.route('/display-users')
def display_users():
    response = table.scan()
    for email in response["Items"]:
        print_game(game)
        print(" \n")
    # hard code a value to the users_list;
    # note that this could have been a result from an SQL query :) 
    users_list = (('John','Doe','Comedy'),('Jane', 'Doe','Drama'))
    return render_template('display_users.html', users = users_list)

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
