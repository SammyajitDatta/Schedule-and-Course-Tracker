# Allows access to environment variables
import os
#Imports library to interact with MySQL database
import mysql.connector

class Configuration:
    # Obtains enviornment variable values, if not found, they are given default values 
    # localhost is the default hostname for locally run database and root is default admin username for MySQL databases
    # Password and database are custom created for my personal usage
    host = os.environ.get("databaseHost", "localhost")
    user = os.environ.get("databaseUser", "root")
    password = os.environ.get("databasePassword", "Satattya1234")
    database = os.environ.get("databaseName", "schedulesAndNotesDatabase")

# Creates a connection object to the database for our program to use
def getDatabaseConnection():
    return mysql.connector.connect(    
        host=Configuration.host,
        user=Configuration.user,
        password=Configuration.password,
        database=Configuration.database,
    )
