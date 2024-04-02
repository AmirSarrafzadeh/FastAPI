import requests
import datetime
import pandas as pd
import streamlit as st


# Backend API URL
backend_url = "http://localhost:8000"

def fetch_students_data():
    response = requests.get(f"{backend_url}/students/")
    if response.status_code == 200:
        students = response.json()
        return students
    else:
        st.error("Failed to fetch students data")


def fetch_lessons_data():
    response = requests.get(f"{backend_url}/lessons/")
    if response.status_code == 200:
        lessons = response.json()
        return lessons
    else:
        st.error("Failed to fetch lessons data")

def register_student():
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day
    st.subheader("Student Registration")
    name = st.text_input("Name")
    surname = st.text_input("Surname")
    age = st.date_input("Select a date",
                                  min_value=datetime.date(1900, 1, 1),
                                  max_value=datetime.date(current_year, current_month, current_day))
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    nationality = st.text_input("Nationality")
    field_of_studying = st.text_input("Field of Studying")

    if st.button("Register"):

        student_data = {
            'name': name,
            'surname': surname,
            'age': str(age),
            'sex': sex,
            'nationality': nationality,
            'field_of_studying': field_of_studying
        }

        response = requests.post(f"{backend_url}/register_student/", json=student_data)
        if response.status_code == 200:
            st.success("Student registered successfully")
        else:
            st.write(response.status_code)
            st.error("Failed to register student")


def main():
    st.title("University Portal Simulator")

    page = st.sidebar.selectbox("Select Page", ["Register Student", "Add Lesson", "View Students", "View Lessons"])

    if page == "Register Student":
        register_student()
    elif page == "Add Lesson":
        st.subheader("Add Lesson")
        name = st.text_input("Name")
        field_of_studying = st.text_input("Field of Studying")

        if st.button("Add"):
            lesson_data = {
                "name": name,
                "field_of_studying": field_of_studying
            }
            response = requests.post(f"{backend_url}/add_lesson/", json=lesson_data)
            if response.status_code == 200:
                st.success("Lesson added successfully")
            else:
                st.error("Failed to add lesson")
    elif page == "View Students":
        response = requests.get(f"{backend_url}/students/")
        if response.status_code == 200:
            students = fetch_students_data()
            if not students:
                st.markdown("""
                                <div style="padding: 10px; background-color: #ADD8E6; border-radius: 5px;">
                                    <p style="color: #FF0000; margin: 0;">No students found</p>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                df_students = pd.DataFrame(students)
                st.dataframe(df_students)
        else:
            st.error("Failed to fetch students data")
    elif page == "View Lessons":
        response = requests.get(f"{backend_url}/lessons/")
        if response.status_code == 200:
            lessons = fetch_lessons_data()
            if not lessons:
                st.markdown("""
                                <div style="padding: 10px; background-color: #708090; border-radius: 5px;">
                                    <p style="color: #32CD32; margin: 0;">No lessons found</p>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                df_lessons = pd.DataFrame(lessons)
                st.dataframe(df_lessons)
        else:
            st.error("Failed to fetch lessons data")

if __name__ == "__main__":
    main()
