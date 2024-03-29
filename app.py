from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_cors import CORS
from datetime import date, datetime
import calendar
import random
from decimal import Decimal
import sys
import json
from datetime import timedelta

import data_importer

app = Flask(__name__, static_url_path="/static")
CORS(app)


def timedelta_to_str(td: timedelta) -> str:
    """
    Converts a timedelta object to a string representation.
    Format: 'HH:MM:SS'
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@app.route("/")
def index():
    return "Backend is running"


@app.route("/get_lat_long", methods=["GET"])
def get_lat_long():
    test_lat = 45.5053
    test_long = -73.5775

    return jsonify({"lat": test_lat, "lng": test_long})


@app.route("/get_data", methods=["GET"])
def get_data():
    # Get date and time from query parameters
    test_day = request.args.get("day")
    test_time = request.args.get("time")

    # Hardcode test.
    # test_day = "Monday"
    # test_time = "01:30"

    if not test_day or not test_time:
        return jsonify({"error": "Day and time parameters are required"}), 400

    connection = data_importer.connect_to_database()
    if connection:
        courses_data = data_importer.get_courses_at_given_time_with_location(
            connection, test_day, test_time
        )
        # Adjust coordinates for courses in the same building
        seen_locations = {}
        valid_courses = [
            course
            for course in courses_data
            if course["latitude"] is not None and course["longitude"] is not None
        ]

        if not valid_courses:
            print("No courses with valid coordinates to display on the map.")
            sys.exit(1)
        for course in valid_courses:
            # timedelta not JSON serializable, convert to string
            course["time_start"] = timedelta_to_str(course["time_start"])
            course["time_end"] = timedelta_to_str(course["time_end"])

            loc_key = (course["latitude"], course["longitude"])
            if loc_key in seen_locations:
                # Apply a small random offset, converting the offset to Decimal
                offset_lat = Decimal(random.uniform(-0.0001, 0.0001))
                offset_lon = Decimal(random.uniform(-0.0001, 0.0001))
                course["latitude"] += offset_lat
                course["longitude"] += offset_lon
            else:
                seen_locations[loc_key] = True

        return jsonify(valid_courses)
        try:
            return json.dumps(valid_courses)
        except TypeError as e:
            print(e)
            print("Error converting to JSON")
            sys.exit(1)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
