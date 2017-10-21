#!/usr/bin/env python3

from flask import Flask, render_template
from data import Articles

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def about():
    return render_template('articles.html', articles= Articles())

if __name__ == '__main__':
    app.run(debug=True)
