from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from Flask!</h1>'