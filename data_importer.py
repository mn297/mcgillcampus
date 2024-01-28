import csv
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import geo_locate
import os
from dotenv import load_dotenv
import ratemyprofessor
import json

load_dotenv()


def process_time_range(time_range_str):
    try:
        # Check if the time range is not a standard time format (e.g., 'TBA')
        if "TBA" in time_range_str.upper() or not "-" in time_range_str:
            return None, None

        # Split the time range into start and end times
        start_time_str, end_time_str = time_range_str.split("-")

        # Convert time strings into time objects
        start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p").time()
        end_time = datetime.strptime(end_time_str.strip(), "%I:%M %p").time()
        return start_time, end_time
    except ValueError:
        print(f"Error while processing time range: {time_range_str}")
        return None, None


# Fetching environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


def connect_to_database():
    try:
        # connection = mysql.connector.connect(
        #     host="localhost",  # Replace with your host name
        #     database="campus_w24",  # Replace with your database name
        #     user="root",  # Replace with your username
        #     password= db_password,
        # )  # Replace with your password

        connection = mysql.connector.connect(
            host=db_host, user=db_user, password=db_password, database=db_name
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


def drop_tables(connection):
    cursor = connection.cursor()

    # SQL to drop sections table
    drop_sections_table = "DROP TABLE IF EXISTS campus_w24.sections;"

    # SQL to drop locations table
    drop_locations_table = "DROP TABLE IF EXISTS campus_w24.locations;"

    # SQL to drop courses table
    drop_courses_table = "DROP TABLE IF EXISTS campus_w24.courses;"

    try:
        # Execute the SQL commands in the reverse order of table creation
        cursor.execute(drop_sections_table)
        cursor.execute(drop_locations_table)
        cursor.execute(drop_courses_table)
        connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()


# TODO parametrize database name
def create_table_if_not_exists(connection):
    cursor = connection.cursor()

    # SQL to create courses table if it does not exist
    create_courses_table = """
    CREATE TABLE IF NOT EXISTS campus_w24.courses (
        crn VARCHAR(255) PRIMARY KEY,
        subject VARCHAR(255),
        course VARCHAR(255),
        title VARCHAR(255),
        credits DECIMAL(5, 3)
    );
    """

    # SQL to create locations table
    create_locations_table = """
    CREATE TABLE IF NOT EXISTS campus_w24.locations (
        location_id INT AUTO_INCREMENT PRIMARY KEY,
        location_name VARCHAR(255),  -- e.g., "WONG 1050"
        building VARCHAR(255),      -- e.g., "WONG"
        search_keyword VARCHAR(255), -- e.g., "M. H. Wong Building"
        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6)
    );
    """

    # SQL to create sections table if it does not exist
    # TODO cleanup, Subject and Course should be foreign keys
    # TODO capacity, wl_capacity, wl_actual, wl_remaining should be integers
    create_sections_table = """
    CREATE TABLE IF NOT EXISTS campus_w24.sections (
        crn VARCHAR(255),
        subject VARCHAR(255),
        course VARCHAR(255),
        section VARCHAR(255),
        type VARCHAR(255),
        instructor VARCHAR(255),
        days VARCHAR(255),
        time VARCHAR(255),
        time_start TIME,
        time_end TIME,
        location_id INT,
        capacity VARCHAR(255),
        wl_capacity VARCHAR(255),
        wl_actual VARCHAR(255),
        wl_remaining VARCHAR(255),
        date VARCHAR(255),
        PRIMARY KEY (crn, section),
        FOREIGN KEY (crn) REFERENCES campus_w24.courses(crn),
        FOREIGN KEY (location_id) REFERENCES campus_w24.locations(location_id)
    );
    """

    # Execute the SQL commands, ORDER MATTERS!
    cursor.execute(create_courses_table)
    cursor.execute(create_locations_table)
    cursor.execute(create_sections_table)
    cursor.close()


def insert_course_data(connection, course_data, row_number):
    try:
        cursor = connection.cursor()
        # Parse and clean the 'Credits' data
        credits_str = course_data["credits"].split("/")[
            0
        ]  # Taking the first part before '/'
        credits = float(credits_str) if credits_str else 0.0

        # Update the course_data dictionary with the cleaned credits
        course_data["credits"] = credits

        query = """INSERT INTO courses (crn, subject, course, title, credits) 
                   VALUES (%(crn)s, %(subject)s, %(course)s, %(title)s, %(credits)s) 
                   ON DUPLICATE KEY UPDATE title=VALUES(title), credits=VALUES(credits);"""
        cursor.execute(query, course_data)
        connection.commit()
    except Error as e:
        print(f"Error while inserting course data at CSV row {row_number}: {e}")


def insert_location_data(connection, location_name):
    try:
        cursor = connection.cursor()
        # Check if the location already exists
        cursor.execute(
            "SELECT location_id FROM locations WHERE location_name = %s",
            (location_name,),
        )
        location_id = cursor.fetchone()
        if location_id:
            return location_id[0]  # Return existing LocationID

        # If not, insert the new location
        cursor.execute(
            "INSERT INTO locations (location_name) VALUES (%s)", (location_name,)
        )
        connection.commit()
        return cursor.lastrowid  # Return the new LocationID
    except Error as e:
        print(f"Error while inserting location data: {e}")
        return None


def update_db_search_keyword(connection, csv_file_path):
    with open(csv_file_path, mode="r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            location_name = row["building"]
            search_keyword = row["search_keyword"]
            try:
                cursor = connection.cursor()
                # Extract the building code (assumed to be the first word of the location_name)
                building_code = location_name.split()[0]

                # Update database, change existing location with building and search_keyword using location_name
                cursor.execute(
                    "UPDATE locations SET building = %s, search_keyword = %s WHERE location_name LIKE %s",
                    (building_code, search_keyword, location_name + "%"),
                )
                connection.commit()
                print(f"Location data updated for: {location_name}")
            except Error as e:
                print(f"Error while updating location data: {e}")


# TODO support for google maps API
def update_db_location_coordinates(connection):
    try:
        cursor = connection.cursor()
        # Fetch unique buildings along with their corresponding search_keywords
        cursor.execute(
            # "SELECT DISTINCT building, search_keyword FROM locations WHERE latitude IS NULL OR longitude IS NULL"
            "SELECT DISTINCT building, search_keyword FROM locations"
        )
        unique_buildings = cursor.fetchall()

        for building, search_keyword in unique_buildings:
            if search_keyword:  # Ensure search_keyword is not None or empty
                latitude, longitude = geo_locate.fetch_coordinates(
                    search_keyword + ", Montreal"
                )
                print(f"Coordinates for '{search_keyword}': {latitude}, {longitude}")
                if latitude and longitude:
                    # Update database with the coordinates
                    update_query = "UPDATE locations SET latitude = %s, longitude = %s WHERE building = %s"
                    cursor.execute(update_query, (latitude, longitude, building))
                    connection.commit()
                    print(
                        f"Updated all locations with building '{building}' '{search_keyword}' to coordinates: {latitude}, {longitude}"
                    )
                else:
                    print(
                        f"Could not find coordinates for building '{building}' with search keyword '{search_keyword}'"
                    )
            else:
                print(f"No search keyword for building '{building}'")

    except Error as e:
        print(f"Error updating location coordinates: {e}")


def cleanup_tables(connection):
    try:
        cursor = connection.cursor()

        # Find the location_id for 'TBA' locations
        cursor.execute("SELECT location_id FROM locations WHERE location_name = 'TBA'")
        tba_location_id = cursor.fetchone()

        # List of tables to clean up (add or remove table names as necessary)
        tables_to_cleanup = ["sections"]

        # Delete rows from each table where location_id matches TBA location_id, or time/days are 'TBA'
        for table in tables_to_cleanup:
            if tba_location_id:
                tba_location_id_value = tba_location_id[0]
                delete_query = f"DELETE FROM {table} WHERE location_id = %s OR time = 'TBA' OR days = 'TBA'"
                cursor.execute(delete_query, (tba_location_id_value,))
            else:
                delete_query = f"DELETE FROM {table} WHERE time = 'TBA' OR days = 'TBA'"
                cursor.execute(delete_query)

            connection.commit()
            print(f"Cleaned up table '{table}' for TBA locations and TBA times/days.")

    except Error as e:
        print(f"Error during cleanup: {e}")


def insert_section_data(connection, section_data, row_number):
    try:
        cursor = connection.cursor()
        location_id = insert_location_data(connection, section_data["location_name"])

        # Process the time range from the 'time' key in section_data
        time_start, time_end = process_time_range(section_data["time"])

        # Build the data tuple for insertion, ensuring all keys match your table columns
        section_data_tuple = (
            section_data["crn"],
            section_data["subject"],
            section_data["course"],
            section_data["section"],
            section_data["type"],
            section_data["instructor"][:255],  # Truncate if necessary
            section_data["days"],
            section_data["time"],
            time_start,  # Start Time
            time_end,  # End Time
            location_id,
            section_data["capacity"],
            section_data["wl_capacity"],
            section_data["wl_actual"],
            section_data["wl_remaining"],
            section_data["date"],
        )

        query = """INSERT INTO sections (crn, subject, course, section, type, instructor, days, time, time_start, time_end, location_id, capacity, wl_capacity, wl_actual, wl_remaining, date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                   ON DUPLICATE KEY UPDATE 
                    type=VALUES(type), 
                    instructor=VALUES(instructor), 
                    days=VALUES(days), 
                    time=VALUES(time),
                    time_start=VALUES(time_start), 
                    time_end=VALUES(time_end), 
                    location_id=VALUES(location_id),
                    capacity=VALUES(capacity),
                    wl_capacity=VALUES(wl_capacity),
                    wl_actual=VALUES(wl_actual),
                    wl_remaining=VALUES(wl_remaining),  
                    date=VALUES(date);"""
        cursor.execute(query, section_data_tuple)
        connection.commit()
    except Error as e:
        print(f"Error while inserting section data at CSV row {row_number}: {e}")


def is_title_row(row):
    return row[0] == "CRN"


def is_valid_row(row):
    return len(row) > 5


day_formats = {
    "Monday": "M",
    "Tuesday": "T",
    "Wednesday": "W",
    "Thursday": "R",
    "Friday": "F",
    # Add more mappings as needed
}
def parse_name(name):
    parsed_name = name.split()
    return parsed_name

def get_courses_at_given_time_with_location(connection, given_day, given_time):
    try:
        cursor = connection.cursor()
        # Format the day to match the format used in your database (e.g., 'T' for Tuesday)
        day_format = day_formats[given_day]

        # Modify the query to join with the locations table and select latitude and longitude
        query = """
                SELECT sections.*, locations.location_name, locations.latitude, locations.longitude 
                FROM sections 
                INNER JOIN locations ON sections.location_id = locations.location_id
                WHERE sections.days LIKE %s 
                AND sections.time_start <= %s 
                AND sections.time_end >= %s
                """
        cursor.execute(query, ("%" + day_format + "%", given_time, given_time))

        # Fetch column names from cursor.description
        columns = [col[0] for col in cursor.description]
        prof_ratings = json.load(open("profratings.json"))
        courses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        for course in courses:
            parsed_key = parse_name(course["instructor"])
            for prof in prof_ratings:
                #print(str(parsed_key) + "?" + prof + "\n")
                parsed_prof = parse_name(prof)
                if parsed_key[0] == (parsed_prof[0] and parsed_key[-1] == parsed_prof[-1]) or (parsed_key[-1] == parsed_prof[0] and parsed_key[0] == parsed_prof[-1]) or (parsed_key[0] == parsed_prof[0] and parsed_key[1] == parsed_prof[1]) or (parsed_key[0] == parsed_prof[1] and parsed_key[1] == parsed_prof[0]):
                    print("Match!\n")
                    course["rating"] = prof_ratings[prof]
        #print(courses)
        return courses  # Returns a list of courses with location data as dictionaries

    except Error as e:
        print(f"Error: {e}")
        return []


def get_courses_at_given_time_with_location_for_day(connection, given_day):
    try:
        cursor = connection.cursor()
        # Format the day to match the format used in your database (e.g., 'T' for Tuesday)
        day_format = day_formats[given_day]

        # Modify the query to join with the locations table and select latitude and longitude
        query = """
                SELECT sections.*, locations.location_name, locations.latitude, locations.longitude 
                FROM sections 
                INNER JOIN locations ON sections.location_id = locations.location_id
                WHERE sections.days LIKE CONCAT('%', %s, '%')
                """
        cursor.execute(query, (day_format,))

        # Fetch column names from cursor.description
        columns = [col[0] for col in cursor.description]

        courses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return courses  # Returns a list of courses with location data as dictionaries

    except Error as e:
        print(f"Error: {e}")
        return []


# CSV Column Index Mapping:
# 0 = CRN (Course Reference Number)
# 1 = Subject (Subject Code)
# 2 = Course (Course Number)
# 3 = Section (Section Number)
# 4 = Type (Type of the Course, e.g., Lecture, Seminar)
# 5 = Credits (Number of Credits for the Course)
# 6 = Title (Title of the Course)
# 7 = Days (Days when the Course is conducted)
# 8 = Time (Time of the Course)
# 9 = Capacity (Maximum number of students that can enroll)
# 10 = WL Capacity (Waitlist Capacity)
# 11 = WL Actual (Actual number of students on the Waitlist)
# 12 = WL Remaining (Remaining spots on the Waitlist)
# 13 = Instructor (Name of the Instructor)
# 14 = Date (Date range for the Course, format MM/DD-MM/DD)
# 15 = Location (Location of the Course)
# 16 = Status (Status of the Course, e.g., Active, Cancelled)


def import_csv_data(connection, csv_file_path):
    with open(csv_file_path, mode="r", errors="replace") as file:
        csv_reader = csv.reader(file)
        for row_number, row in enumerate(csv_reader, start=1):  # Start counting from 1
            if is_title_row(row) or not is_valid_row(row):
                continue
            section_data = {
                "crn": row[0],
                "subject": row[1],
                "course": row[2],
                "section": row[3],
                "type": row[4],
                "credits": row[5],
                "title": row[6],
                "days": row[7],
                "time": row[8],
                "capacity": row[9],
                "wl_capacity": row[10],
                "wl_actual": row[11],
                "wl_remaining": row[12],
                "instructor": row[13],
                "date": row[14],
                "location_name": row[15],
            }
            insert_course_data(connection, section_data, row_number)
            insert_section_data(connection, section_data, row_number)
def scrape_profs(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT instructor FROM sections")
        unique_profs = cursor.fetchall()
        school = ratemyprofessor.get_school_by_name("McGill University")
        profs = {}
        counter = 0
        for prof_tuple in unique_profs:
            for prof in prof_tuple:
                if prof is not None:
                    professor = ratemyprofessor.get_professor_by_school_and_name(school, prof)
                    if professor is not None:
                        print(str(counter) + ":\n")
                        print("Name: " + professor.name + "\n")
                        print("Rating: " + str(professor.rating) + "\n")
                        profs.update({professor.name: professor.rating})
                        counter += 1
        with open ("profratings.json", "w") as outfile:
            json.dump(profs, outfile)

        
        return courses  # Returns a list of courses with location data as dictionaries
    except Error as e:
        print(f"Error: {e}")
        return []


def main():
    connection = connect_to_database()
    if connection is not None:
        drop_tables(connection)
        create_table_if_not_exists(connection)
        import_csv_data(connection, "A_H_W24.csv")
        import_csv_data(connection, "I_Z_W24.csv")
        update_db_search_keyword(connection, "buildings_dict.csv")
        update_db_location_coordinates(connection)
        cleanup_tables(connection)
        connection.close()


if __name__ == "__main__":
    main()