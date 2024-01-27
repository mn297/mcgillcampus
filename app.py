from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route("/")
def index():
    return "Backend is running"
@app.route('/get_lat_long', methods=['GET'])    
def get_lat_long():
    test_lat = 45.5053
    test_long = -73.5775

    return jsonify({'lat': test_lat, 'lng': test_long})

if __name__ == '__main__':
    app.run(port=8000,debug=True)