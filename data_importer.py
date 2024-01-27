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
        # PHASE1
        connection = mysql.connector.connect(
            host="localhost",  # Replace with your host name
            database="campus_w24",  # Replace with your database name
            user="root",  # Replace with your username
            password= db_password,
        )  # Replace with your password
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

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
