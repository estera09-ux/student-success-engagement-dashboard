import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Dashboard")

# login details
username_correct = "admin"
password_correct = "password123"

# weights
exam_weight = 0.7
coursework_weight = 0.3

# grade boundaries
distinction = 70
pass_mark = 40

# required columns
required_columns = ["Student_ID", "Student_Name", "Exam_Mark", "Coursework_Mark"]

# function
def get_performance(grade):
    if grade >= distinction:
        return "Distinction"
    elif grade >= pass_mark:
        return "Pass"
    else:
        return "Fail"

# login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# LOGIN
if st.session_state.logged_in == False:

    st.title("Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == username_correct and pwd == password_correct:
            st.session_state.logged_in = True
            st.success("Logged in")
            st.rerun()
        else:
            st.error("Wrong username or password")

# MAIN APP
else:

    st.title("Student Dashboard")

    file = st.file_uploader("Upload CSV file")

    if file is not None:

        data = pd.read_csv(file)

        # check columns
        missing = []

        for col in required_columns:
            if col not in data.columns:
                missing.append(col)

        if len(missing) > 0:
            st.error("Missing columns: " + ", ".join(missing))
            st.stop()

        # clean exam marks
        data["Exam_Mark"] = pd.to_numeric(data["Exam_Mark"], errors="coerce")
        data["Exam_Mark"] = data["Exam_Mark"].fillna(0)
        data["Exam_Mark"] = data["Exam_Mark"].clip(0, 100)

        # clean coursework marks
        data["Coursework_Mark"] = pd.to_numeric(data["Coursework_Mark"], errors="coerce")
        data["Coursework_Mark"] = data["Coursework_Mark"].fillna(0)
        data["Coursework_Mark"] = data["Coursework_Mark"].clip(0, 100)

        # calculate final grades
        final_grades = []

        for i in range(len(data)):
            exam = data["Exam_Mark"][i]
            coursework = data["Coursework_Mark"][i]

            final = (exam * exam_weight) + (coursework * coursework_weight)
            final_grades.append(final)

        data["Final Grade"] = final_grades

        # assign performance
        performance = []

        for i in range(len(data)):
            grade = data["Final Grade"][i]
            result = get_performance(grade)
            performance.append(result)

        data["Performance"] = performance

        # filter
        option = st.selectbox("Filter results", ["All", "Distinction", "Pass", "Fail"])

        if option != "All":
            data = data[data["Performance"] == option]

        # search
        name = st.text_input("Search student name")

        if name != "":
            data = data[data["Student_Name"].str.contains(name, case=False, na=False)]

        # show results
        st.write("Results table")
        st.dataframe(data)

        # chart
        st.write("Chart")
        counts = data["Performance"].value_counts()
        st.bar_chart(counts)

        # download
        csv = data.to_csv(index=False)
        st.download_button("Download results", csv, "results.csv")

    else:
        st.write("Please upload a CSV file")

    # logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()