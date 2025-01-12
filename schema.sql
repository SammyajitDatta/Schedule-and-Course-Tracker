CREATE DATABASE IF NOT EXISTS schedulesAndNotesDatabase;
USE schedulesAndNotesDatabase;

CREATE TABLE IF NOT EXISTS Schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personName VARCHAR(255) NOT NULL,
    filePath VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Courses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  courseName VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS Notes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  courseID INT,
  filePath VARCHAR(255),
  FOREIGN KEY (courseID) REFERENCES Courses(id)
);