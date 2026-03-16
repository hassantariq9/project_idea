
import streamlit as st
from database.db import read
import plotly.express as px

def analytics_dashboard():
    st.title("Idea Analytics")

    try:
        df = read("SELECT * FROM ideas")
    except:
        st.info("No data yet")
        return

    fig1 = px.histogram(df, x="status", title="Idea Status Distribution")
    st.plotly_chart(fig1)

    fig2 = px.histogram(df, x="student", title="Ideas per Student")
    st.plotly_chart(fig2)
