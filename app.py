from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def index():
    return "Backend is running"

if __name__ == '__main__':
    app.run(port=8000,debug=True)