# Provides access to operating system functionality
import os
# Import Flask components for creating a web app, handling requests, and returning JSON responses
from flask import Flask, request, jsonify
from configAndDatabase import getDatabaseConnection

app = Flask(__name__, static_folder='static')

# Create folders if the folders do not already exist
NOTESFOLDER = os.path.join('static', 'notes')
if not os.path.exists(NOTESFOLDER):
    os.makedirs(NOTESFOLDER)
SCHEDULESFOLDER = os.path.join('static', 'schedules')
if not os.path.exists(SCHEDULESFOLDER):
    os.makedirs(SCHEDULESFOLDER)

@app.route('/api/schedules', methods=['GET'])
def getSchedules():
    # Fetch and return all schedules 

    # Connects to database
    database = getDatabaseConnection()

    # Create a cursor that returns query results as dictionaries
    cursor = database.cursor(dictionary=True)

    # Executes the query to select rows for fetching
    cursor.execute("SELECT * FROM Schedules")

    # Fetches all rows from the schedules table
    rows = cursor.fetchall()

    # Closes cursor to prevent unnecessary resource usage 
    cursor.close()

    #Disconnects from database
    database.close()

    # Updates filepath to include the prefix folder of the images
    for row in rows:
        row['filePath'] = f'/static/{row["filePath"]}'  
    
    # Sends both the data and success status of the call back to client in terminal.  
    return jsonify(rows), 200


@app.route('/api/schedules', methods=['POST'])
def uploadSchedule():
    #Upload schedule PNG

    personName = request.form.get('personName')
    file = request.files.get('file')

    # Gives a bad request message to the user in the terminal letting them know what they need to fill in
    if not personName or not file:
        return jsonify({'error': 'personName and file are required'}), 400
    
    # Gives a bad request message to the user in the terminal letting them know only pngs are accepted
    if not file.filename.lower().endswith('.png'):
        return jsonify({'error': 'Only PNG files allowed'}), 400

    filePath = os.path.join(SCHEDULESFOLDER, file.filename)
    # Saves the file to the specified file path location
    file.save(filePath)

    databasePath = f'schedules/{file.filename}'

    # Connects to database
    database = getDatabaseConnection()
    
    # Create a cursor to interact with the database
    cursor = database.cursor()
    
    # Stages changes to the database
    query = "INSERT INTO Schedules (personName, filePath) VALUES (%s, %s)"
    cursor.execute(query, (personName, databasePath))

    # Officially saves the changes to the database
    database.commit()

    # Closes cursor to prevent unnecessary resource usage 
    cursor.close()

    #Disconnects from database
    database.close()

    # Sends both the data and success status of the call back to client in terminal.  
    return jsonify({'message': 'Schedule uploaded'}), 201


@app.route('/api/schedules/<int:scheduleID>', methods=['DELETE'])
def deleteSchedule(scheduleID):
    # Delete schedule via ID and the associated file.

    # Connect to the database
    database = getDatabaseConnection()

    # Create a cursor that returns query results as dictionaries
    cursor = database.cursor(dictionary=True)
    
    # Select the file via id we want to delete from database and fetch it
    cursor.execute("SELECT filePath FROM Schedules WHERE id=%s", (scheduleID,))
    row = cursor.fetchone()

    # If the schedule does not exist via the id, send a not found error message
    if not row:
        # Closes cursor to prevent unnecessary resource usage 
        cursor.close()
        
        #Disconnects from database
        database.close()

        return jsonify({'error': 'Schedule not found'}), 404

    filePath = row['filePath']
    fullFilePath = os.path.join('static', filePath)  

    # Stages changes to the database 
    cursor.execute("DELETE FROM Schedules WHERE id=%s", (scheduleID,))
    
    # Commits changes to the database
    database.commit()
    
    # Closes cursor to prevent unnecessary resource usage 
    cursor.close()
    
    # Disconnects from database
    database.close()

    # Deletes image from schedules folder
    if os.path.exists(fullFilePath):
        os.remove(fullFilePath)

    # Sends both the data and success status of the call  back to client in terminal.  
    return jsonify({'message': 'Schedule deleted'}), 200

@app.route('/api/notes', methods=['GET'])
def getCoursesAndNotes():
    # Get courses and their assoicated notes

    # Connect to the database
    database = getDatabaseConnection()

    # Create a cursor that returns query results as dictionaries
    cursor = database.cursor(dictionary=True)

    # Select and fetch all courses
    cursor.execute("SELECT * FROM Courses")
    courses = cursor.fetchall()

    # Iterate through all the courses
    for course in courses:
        
        # Select and fetch id and file path from notes table based on the courseID
        cursor.execute("SELECT id, filePath FROM Notes WHERE courseID=%s", (course['id'],))
        notes = cursor.fetchall()

        # Update file path of all notes
        for note in notes:
            note['filePath'] = f"/static/{note['filePath']}" 

        # Adds all associated notes to the course as a new 'notes' key
        # Used in fetch courses
        course['notes'] = notes

    # Closes cursor to prevent unnecessary resource usage 
    cursor.close()
    
    # Disconnects from database
    database.close()

    # Sends both the data and success status of the call  back to client in terminal.    
    return jsonify(courses), 200


@app.route('/api/notes', methods=['POST'])
def uploadNote():
    # Upload notes

    courseName = request.form.get('courseName')
    file = request.files.get('file')

    # Gives a bad request message to the user in the terminal letting them know what they need to fill in
    if not courseName or not file:
        return jsonify({'error': 'courseName and file are required'}), 400
    
    # Gives a bad request message to the user in the terminal letting them know only pngs and pdfs are accepted
    if not file.filename.lower().endswith(('.png','.pdf')):
        return jsonify({'error': 'Only image and PDF files allowed'}), 400

    filePath = os.path.join(NOTESFOLDER, file.filename)
    # Saves the file to the specified file path location
    file.save(filePath)

    databasePath = f'notes/{file.filename}'  

    # Connects to the database
    database = getDatabaseConnection()

    # Create a cursor that returns query results as dictionaries
    cursor = database.cursor(dictionary=True)

    # Select and fetch course ID from appropriate course 

    cursor.execute("SELECT id FROM Courses WHERE courseName=%s", (courseName,))
    existingCourse = cursor.fetchone()

    # If course already exists, the new note just uses the existing ID
    if existingCourse:
        courseID = existingCourse['id']
    else:
        # IF course does not exist, we stage and save changes of adding new course to database.
        cursor.execute("INSERT INTO Courses (courseName) VALUES (%s)", (courseName,))
        database.commit()

        # The course id now becomes the very last id of the table as the new note belongs to the newest course
        courseID = cursor.lastrowid

    # Stage and save changes to database. 
    cursor.execute("INSERT INTO Notes (courseID, filePath) VALUES (%s, %s)", (courseID, databasePath))
    database.commit()

    # Closes cursor to prevent unnecessary resource usage 
    cursor.close()
    
    # Disconnects from database
    database.close()

    # Sends both the data and success status of the call  back to client in terminal.    
    return jsonify({'message': 'Note file uploaded'}), 201

@app.route('/api/notes/<int:noteID>', methods=['DELETE'])
def deleteNote(noteID):
    # Deletes not from the courses, if number of note reaches 0, courses is also deleted. 

    # Connects to the database
    database = getDatabaseConnection()

    # Create a cursor that returns query results as dictionaries
    cursor = database.cursor(dictionary=True)

    # Select and fetch information of note with specified ID
    cursor.execute("SELECT filePath, courseID FROM Notes WHERE id=%s", (noteID,))
    row = cursor.fetchone()


    # If the schedule does not exist via the id, send a not found error message
    if not row:
        # Closes cursor to prevent unnecessary resource usage 
        cursor.close()
        
        #Disconnects from database
        database.close()

        return jsonify({'error': 'Note not found'}), 404

    filePath = row['filePath']
    courseID = row['courseID']
    fullFilePath = os.path.join('static', filePath)

    # Stages and saves changes to the database 
    cursor.execute("DELETE FROM Notes WHERE id=%s", (noteID,))
    database.commit()

    # Query to count the number of notes associated with the specified courseID
    cursor.execute("SELECT COUNT(*) AS counters FROM Notes WHERE courseID=%s", (courseID,))
    numberOfNotes = cursor.fetchone()['counters']

    # If a course has no notes, delete the course 
    if numberOfNotes == 0:
        # Stages and saves changes to the database 
        cursor.execute("DELETE FROM Courses WHERE id=%s", (courseID,))
        database.commit()

    # Closes cursor to prevent unnecessary resource usage 
    cursor.close()
    
    #Disconnects from database
    database.close()

    # Deletes note from schedules folder
    if os.path.exists(fullFilePath):
        os.remove(fullFilePath)

    # Sends both the data and success status of the call  back to client in terminal. 
    return jsonify({'message': 'Note deleted'}), 200

# Opens up to index.html on initial launch
@app.route('/')
def index():
    return app.send_static_file('index.html')  

# Runs application on port 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)

