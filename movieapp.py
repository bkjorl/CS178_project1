from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import execute_query, table
import pymysql
import creds 
import boto3

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

#app routes
#home page
@app.route('/')
def home():
    return render_template('home.html')

#user pages
#add user page
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

        #exception created with the help of Chatgpt
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

#reccomendation pages
#Genre Recommendations
@app.route("/genre_rec", methods=["GET", "POST"])
def genre_rec():
    movies = []
    genre = None

    if request.method == "POST":
        genre = request.form.get("genre")

        if not genre:
            flash("please input a genre", "danger")
            return redirect(url_for("genre_rec"))

        #the parameters part of this query and the exceptions section were created with the help of Chatgpt
        try:
            query = """
                SELECT title, genre_name, release_date
                FROM movie JOIN movie_genres USING(movie_id) JOIN genre USING(genre_id)
                WHERE genre_name = %s
                ORDER BY release_date DESC
                LIMIT 10
            """
            movies = execute_query(query, (genre,))
        except Exception as e:
            flash("Error fetching movies by genre.", "danger")
            print("Query error:", e)

    return render_template("genre_rec.html", movies=movies, genre=genre)

#User Reccomentation
@app.route("/personal_rec", methods=["GET", "POST"])
def personal_rec():
    genre = None
    movies = []

    if request.method == 'POST':
        email = request.form.get("email") 

        if not email:
            flash("please input an email.", "danger")
            return redirect(url_for("personal_rec"))

        #these exceptions were created with the help of Chatgpt
        try:
            user = table.get_item(Key={'Email': email})
            if 'Item' in user:
                genre = user['Item'].get('Genre')
            else:
                flash("Email not found in user database.", "warning")
        except Exception as e:
            flash("Error accessing user data.", "danger")
            print("DynamoDB error:", e)

        #the parameters part of this query was created with the help of Chatgpt
        if genre:
            query = """
                SELECT title, genre_name, release_date
                FROM movie 
                JOIN movie_genres USING(movie_id) 
                JOIN genre USING(genre_id)
                WHERE genre_name = %s
                ORDER BY release_date
                LIMIT 10
            """
            params = (genre,)

        movies = execute_query(query, params)

    return render_template("personal_rec.html", movies = movies, genre = genre)

#additional homepages that link to user pages and reccommendation pages
#user homepage
@app.route('/user_home')
def user_home():
    return render_template('user_home.html')

#recommendation homepage
@app.route('/recommendation_home')
def recommendation_home():
    return render_template('recommendation_home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)