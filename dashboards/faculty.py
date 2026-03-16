
import streamlit as st
from database.db import read
from utils.heatmap import heatmap
from ai.similarity import similarity_matrix

def faculty_dashboard():
    st.title("Faculty Dashboard")

    try:
        df = read("SELECT * FROM ideas")
    except:
        st.info("No ideas yet")
        return

    st.subheader("Submitted Ideas")
    st.dataframe(df)

    texts = (df["title"] + " " + df["description"]).tolist()

    if len(texts) > 1:
        sim = similarity_matrix(texts)
        st.subheader("Duplicate Detection Heatmap")
        st.plotly_chart(heatmap(sim))
