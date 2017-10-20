#!/usr/bin/env python3

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'hi man'

if name__ == '__main__':
    app.run()
