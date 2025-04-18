from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
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
@app.route('/')
def home():
    return render_template('home.html')

#add user page
    #add user function and then redirect to home page
@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        genre = request.form['genre']
        
        table.put_item (
            Item={
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "Genre": genre,
            }
        )
        
        flash('User added successfully!', 'success')
        return redirect(url_for('home'))
    else:
        return render_template('add_user.html')
    
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

#update user    
@app.route('/update-user', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        email = request.form['email']
        genre = request.form['genre']

        try:
            table.update_item(
                Key={'Email': email},
                UpdateExpression='SET Genre = :g',
                ExpressionAttributeValues={':g': genre}
            )
            flash('User updated successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            print("Update error:", e)
            flash('Error updating user.', 'danger')
            return redirect(url_for('home'))

    else:
        return render_template('update_user.html')
    
#display all users
@app.route('/display-users')
def display_users():
    try:
        response = table.scan()
        users = response.get('Items', [])
        return render_template('display_users.html', users=users)

    except Exception as e:
        print("Scan error:", e)
        flash('Could not load users.', 'danger')
        return redirect(url_for('home'))


#user homepage
@app.route('/user_home')
def user_home():
    return render_template('user_home.html')

#recommendation homepage
@app.route('/recommendation_home')
def recommendation_home():
    return render_template('recommendation_home.html')



























    



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
