import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

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

students_db = []
lessons_db = []

@app.post("/register_student/")
def register_student(student: Student):
    students_db.append(student)
    return {"message": "Student registered successfully"}

@app.post("/add_lesson/")
def add_lesson(lesson: Lesson):
    lessons_db.append(lesson)
    return {"message": "Lesson added successfully"}

@app.get("/students/")
def get_students():
    if not students_db:
        return
    return students_db

@app.get("/lessons/")
def get_lessons():
    if not lessons_db:
        return
    return lessons_db

# Run the FastAPI app with:
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
