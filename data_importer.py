import csv
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import geo_locate
import os


# Fetching environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv('DB_PASSWORD')
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

def main():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM location")
        result = cursor.fetchall()
        for row in result:
            print(row)
        cursor.close()
        connection.close()
    else:
        print("Error while connecting to MySQL")



if __name__ == "__main__":
    main()
