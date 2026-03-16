
import streamlit as st
import pandas as pd
from database.db import read, write
from ai.similarity import detect_duplicate
from datetime import datetime

def student_dashboard(user):
    st.title("Student Idea Submission")

    title = st.text_input("Project Title")
    desc = st.text_area("Description")

    if st.button("Submit Idea"):
        try:
            df = read("SELECT title,description FROM ideas")
            existing = (df["title"] + " " + df["description"]).tolist()
        except:
            existing = []

        text = title + " " + desc
        dup, score = detect_duplicate(text, existing)

        status = "Duplicate" if dup else "Pending"
        idea = pd.DataFrame([[user,title,desc,str(datetime.now()),status,score]],
                            columns=["student","title","description","timestamp","status","similarity"])

        write(idea,"ideas")

        if dup:
            st.error("Idea rejected due to similarity")
        else:
            st.success("Idea submitted successfully")

    try:
        myideas = read(f"SELECT * FROM ideas WHERE student='{user}'")
        st.subheader("Your Ideas")
        st.dataframe(myideas)
    except:
        pass
