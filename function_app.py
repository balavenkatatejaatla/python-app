import logging
import os
import mysql.connector
from mysql.connector import Error
from typing import List
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(user="mysqladmin", password="Password@123", host="testmysqlflex.mysql.database.azure.com", port=3306, database="test", ssl_disabled=False)
    #return mysql.connector.connect(str(os.environ["MySQLConnectionString"]))
    # try:
    #     connection = mysql.connector.connect(
    #         host=os.environ.get("MySQLConnectionString")	
    #     )
    #     return connection
    # except mysql.connector.Error as e:
    #     return None

# Function to add a student to the database
def add_student(student_data):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        query = "INSERT INTO students (student_id, student_name, student_age, student_addr, student_percent, student_qual, student_year_passed) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, student_data)
        
        connection.commit()
        cursor.close()
        connection.close()

        return "Student added successfully"
    except Error as e:
        return f"Error adding student: {e}"

# Function to retrieve all students from the database
def get_students():
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM students"
        cursor.execute(query)
        students = cursor.fetchall()

        cursor.close()
        connection.close()

        return students
    except Error as e:
        return f"Error retrieving students: {e}"

# Function to update a student record in the database
def update_student(student_id, student_data):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        query = "UPDATE students SET student_name = %s, student_age = %s, student_addr = %s, student_percent = %s, student_qual = %s, student_year_passed = %s WHERE student_id = %s"
        cursor.execute(query, (student_data['student_name'], student_data['student_age'], student_data['student_addr'], student_data['student_percent'], student_data['student_qual'], student_data['student_year_passed'], student_id))
        
        connection.commit()
        cursor.close()
        connection.close()

        return "Student updated successfully"
    except Error as e:
        return f"Error updating student: {e}"

# Function to delete a student record from the database
def delete_student(student_id):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        query = "DELETE FROM students WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        
        connection.commit()
        cursor.close()
        connection.close()

        return "Student deleted successfully"
    except Error as e:
        return f"Error deleting student: {e}"

# Main Azure Function HTTP trigger
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger", methods=['GET'])
def get_students_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GET method: Retrieving students.')
    
    students = get_students()

    return func.HttpResponse(body=str(students), mimetype="application/json", status_code=200)

@app.route(route="http_trigger", methods=['POST'])
def add_student_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('POST method: Adding a new student.')

    try:
        req_body = req.get_json()

        student_data = (
            req_body.get('student_id'),
            req_body.get('student_name'),
            req_body.get('student_age'),
            req_body.get('student_addr'),
            req_body.get('student_percent'),
            req_body.get('student_qual'),
            req_body.get('student_year_passed')
        )

        result = add_student(student_data)

        return func.HttpResponse(f"Student added successfully: {result}", status_code=200)
    except ValueError as ve:
        return func.HttpResponse("Error processing request. Please provide valid student data in the request body.", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"An error occurred: {e}", status_code=500)

@app.route(route="http_trigger", methods=['PUT'])
def update_student_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PUT method: Updating a student.')

    try:
        student_id = req.params.get('student_id')
        req_body = req.get_json()

        result = update_student(student_id, req_body)

        return func.HttpResponse(f"Student updated successfully: {result}", status_code=200)
    except ValueError as ve:
        return func.HttpResponse("Error processing request. Please provide valid student data and student_id in the request.", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"An error occurred: {e}", status_code=500)

@app.route(route="http_trigger", methods=['DELETE'])
def delete_student_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('DELETE method: Deleting a student.')

    try:
        student_id = req.params.get('student_id')

        result = delete_student(student_id)

        return func.HttpResponse(f"Student deleted successfully: {result}", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"An error occurred: {e}", status_code=500)
    
@app.route(route="http_trigger", methods=['GET'])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    connection = get_mysql_connection()
    
    if connection is not None:
        return func.HttpResponse("MySQL connection established successfully", status_code=200)
    else:
        return func.HttpResponse("Failed to establish MySQL connection", status_code=500)




