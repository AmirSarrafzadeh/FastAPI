import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import logging

app = FastAPI()
logging.basicConfig(filename="file.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection():
    return sqlite3.connect('university.db')

# Create tables if they don't exist
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            age TEXT,
            sex TEXT,
            nationality TEXT,
            field_of_studying TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            field_of_studying TEXT
        )
    ''')
    conn.commit()
    conn.close()

class Student(BaseModel):
    name: str
    surname: str
    age: str
    sex: str
    nationality: str
    field_of_studying: str

class Lesson(BaseModel):
    name: str
    field_of_studying: str

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.post("/register_student/")
def register_student(student: Student):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (name, surname, age, sex, nationality, field_of_studying)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student.name, student.surname, student.age, student.sex, student.nationality, student.field_of_studying))
    conn.commit()
    conn.close()
    return {"message": "Student registered successfully"}

@app.post("/add_lesson/")
def add_lesson(lesson: Lesson):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lessons (name, field_of_studying)
        VALUES (?, ?)
    ''', (lesson.name, lesson.field_of_studying))
    conn.commit()
    conn.close()
    return {"message": "Lesson added successfully"}

@app.get("/students/", response_model=List[Student])
def get_students():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM students
        ''')
        students_data = cursor.fetchall()
        conn.close()

        # Convert fetched data to list of Student objects
        students = []
        for student_data in students_data:
            student = Student(
                name=student_data[1],
                surname=student_data[2],
                age=student_data[3],
                sex=student_data[4],
                nationality=student_data[5],
                field_of_studying=student_data[6]
            )
            students.append(student)

        if not students:
            logging.warning("No students found in the database")
            return []  # Return empty list if no students found
        return students
    except Exception as e:
        logging.error(f"Error fetching students: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch students data")


@app.get("/lessons/", response_model=List[Lesson])
def get_lessons():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM lessons
        ''')
        lessons_datas = cursor.fetchall()
        conn.close()
        all_lessons = []
        for lesson_data in lessons_datas:
            lesson = Lesson(
                name=lesson_data[1],
                field_of_studying=lesson_data[2]
            )
            all_lessons.append(lesson)

        if not all_lessons:
            return []
        return all_lessons

    except Exception as e:
        logging.error(f"Error fetching lessons: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch lessons data")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
